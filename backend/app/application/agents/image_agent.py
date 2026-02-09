"""
Image Generation Agent using LangGraph workflow.

Implements a workflow for generating product images:
Optimize Prompt -> Generate Image -> Persist Asset
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.core.factory import ProviderFactory
from app.domain.entities.generation import GenerationRequest, StreamChunk
from app.domain.entities.image_artifact import ImageArtifact
from app.domain.entities.image_request import ImageGenerationRequest
from app.domain.exceptions import HTTPClientError
from app.domain.interfaces.image_generator import IImageGenerator
from app.interface.ws.socket_manager import socket_manager


logger = logging.getLogger(__name__)


# =============================================================================
# State Definition
# =============================================================================

class ImageAgentState(TypedDict):
    """TypedDict for LangGraph state.
    
    Tracks the workflow progress from prompt optimization to image generation.
    """
    prompt: str                    # 用户原始提示词
    optimized_prompt: str          # DeepSeek 优化后的提示词
    workflow_id: str               # 工作流唯一标识
    current_stage: Optional[str]   # 当前阶段
    image_url: str                 # 生成的图像 URL
    asset_id: Optional[str]        # 持久化的资产 UUID
    width: int                     # 图像宽度
    height: int                    # 图像高度
    error: Optional[str]           # 错误信息


# Workflow state storage for status queries and cancellation
_workflow_states: Dict[str, Dict[str, Any]] = {}
_workflow_tasks: Dict[str, asyncio.Task] = {}


# =============================================================================
# ImageAgent Class
# =============================================================================

class ImageAgent:
    """
    AI agent for generating product images using LangGraph.
    
    Workflow stages:
    1. Optimize Prompt - Use DeepSeek to enhance the user's prompt
    2. Generate Image - Call MCP ImageGenerator to create the image
    3. Persist Asset - Save image metadata to database
    
    Usage:
        agent = ImageAgent()
        result = await agent.run(
            prompt="A red sports car on a mountain road",
            width=512,
            height=512,
        )
    """
    
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 500
    DEFAULT_WIDTH = 512
    DEFAULT_HEIGHT = 512
    
    # Rate limiting for error logs
    _error_log_times: Dict[str, float] = defaultdict(float)
    _error_log_lock: asyncio.Lock = asyncio.Lock()
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        image_generator: Optional[IImageGenerator] = None,
    ):
        """
        Initialize the image generation agent.
        
        Args:
            model: LLM model to use for prompt optimization
            temperature: Generation temperature
            max_tokens: Max tokens for prompt optimization
            image_generator: Image generator implementation (uses factory if None)
        """
        self.model = model or self.DEFAULT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._image_generator = image_generator
        self._checkpointer = MemorySaver()
        self._graph = self._build_graph()
    
    def _get_image_generator(self) -> IImageGenerator:
        """
        Get image generator instance.
        
        Uses injected generator if provided, otherwise uses factory.
        """
        if self._image_generator is not None:
            return self._image_generator
        
        # Use factory to get default generator based on config
        from app.core.image_factory import ImageProviderFactory
        return ImageProviderFactory.get_provider()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        workflow = StateGraph(ImageAgentState)
        
        # Add nodes
        workflow.add_node("optimize_prompt", self.optimize_prompt_node)
        workflow.add_node("generate_image", self.generate_image_node)
        workflow.add_node("persist_asset", self.persist_asset_node)
        
        # Set entry point
        workflow.set_entry_point("optimize_prompt")
        
        # Add edges: Optimize -> Generate -> Persist -> END
        workflow.add_edge("optimize_prompt", "generate_image")
        workflow.add_edge("generate_image", "persist_asset")
        workflow.add_edge("persist_asset", END)
        
        # Compile with checkpointer
        return workflow.compile(checkpointer=self._checkpointer)
    
    @classmethod
    async def _should_log_error(cls, error_key: str) -> bool:
        """Check if enough time has passed since last error log."""
        async with cls._error_log_lock:
            now = time.time()
            cooldown = settings.error_log_cooldown_seconds
            if now - cls._error_log_times[error_key] > cooldown:
                cls._error_log_times[error_key] = now
                return True
            return False
    
    @classmethod
    def get_workflow_status(cls, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow."""
        return _workflow_states.get(workflow_id)
    
    @classmethod
    def cancel_workflow(cls, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        task = _workflow_tasks.get(workflow_id)
        if task and not task.done():
            task.cancel()
            if workflow_id in _workflow_states:
                _workflow_states[workflow_id]["status"] = "cancelled"
            return True
        return False

    # =========================================================================
    # Node implementations - Subtask 1.2, 1.3, 1.4 将在此添加
    # =========================================================================
    
    async def optimize_prompt_node(self, state: ImageAgentState) -> ImageAgentState:
        """
        Optimize Prompt Node: Enhance user prompt using DeepSeek.
        
        Uses DeepSeek to analyze and improve the user's image description
        for better image generation results.
        
        Args:
            state: Current workflow state with user prompt
            
        Returns:
            Updated state with optimized_prompt
        """
        from app.application.agents.prompts import IMAGE_PROMPTS
        
        workflow_id = state["workflow_id"]
        prompt = state["prompt"]
        width = state["width"]
        height = state["height"]
        
        # Update workflow state
        _workflow_states[workflow_id] = {
            "status": "running",
            "current_stage": "optimize_prompt",
            "state": state,
        }
        
        # Emit thought event
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=IMAGE_PROMPTS.optimize_start,
            node_name="optimize_prompt"
        )
        
        try:
            # Emit tool_call event before DeepSeek API call
            await socket_manager.emit_tool_call(
                workflow_id=workflow_id,
                tool_name="deepseek_optimize",
                status="in_progress",
                message="Calling DeepSeek to optimize image prompt"
            )
            
            # Call DeepSeek to optimize the prompt
            generator = ProviderFactory.get_provider("deepseek")
            async with generator:
                response = await generator.generate(
                    GenerationRequest(
                        prompt=IMAGE_PROMPTS.get_optimize_prompt(prompt, width, height),
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    )
                )
                optimized = response.content.strip()
            
            # Emit completion events
            await socket_manager.emit_tool_call(
                workflow_id=workflow_id,
                tool_name="deepseek_optimize",
                status="completed",
                message="Prompt optimization completed"
            )
            
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=IMAGE_PROMPTS.optimize_complete,
                node_name="optimize_prompt"
            )
            
            new_state = {
                **state,
                "optimized_prompt": optimized,
                "current_stage": "optimize_prompt",
            }
            _workflow_states[workflow_id]["state"] = new_state
            
            logger.info(f"Prompt optimized for workflow {workflow_id}")
            return new_state
            
        except HTTPClientError as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="OPTIMIZE_FAILED",
                error_message=str(e)
            )
            raise
    
    async def generate_image_node(self, state: ImageAgentState) -> ImageAgentState:
        """
        Generate Image Node: Call MCP ImageGenerator.
        
        Uses the optimized prompt to generate an image via the MCP client.
        Currently uses MockMCPImageGenerator, will be replaced with real
        MCP client in Story 3.2.
        
        Args:
            state: Current workflow state with optimized_prompt
            
        Returns:
            Updated state with image_url
        """
        from app.application.agents.prompts import IMAGE_PROMPTS
        
        workflow_id = state["workflow_id"]
        optimized_prompt = state["optimized_prompt"]
        width = state["width"]
        height = state["height"]
        
        # Update workflow state
        _workflow_states[workflow_id]["current_stage"] = "generate_image"
        
        # Emit thought event
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=IMAGE_PROMPTS.generate_start,
            node_name="generate_image"
        )
        
        try:
            # Emit tool_call event before image generation
            await socket_manager.emit_tool_call(
                workflow_id=workflow_id,
                tool_name="mcp_image_generator",
                status="in_progress",
                message="Calling MCP ImageGenerator to create image"
            )
            
            # Create image generation request
            request = ImageGenerationRequest(
                prompt=optimized_prompt,
                width=width,
                height=height,
            )
            
            # Call MCP ImageGenerator (using factory/injected generator)
            generator = self._get_image_generator()
            async with generator:
                artifact = await generator.generate(request)
            
            # Update artifact with workflow context
            artifact.original_prompt = state["prompt"]
            artifact.workflow_id = workflow_id
            
            # Emit completion events
            await socket_manager.emit_tool_call(
                workflow_id=workflow_id,
                tool_name="mcp_image_generator",
                status="completed",
                message=f"Image generated: {artifact.url}"
            )
            
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=IMAGE_PROMPTS.generate_complete,
                node_name="generate_image"
            )
            
            new_state = {
                **state,
                "image_url": artifact.url,
                "current_stage": "generate_image",
            }
            _workflow_states[workflow_id]["state"] = new_state
            # Store artifact for persist node
            _workflow_states[workflow_id]["artifact"] = artifact
            
            logger.info(f"Image generated for workflow {workflow_id}: {artifact.url}")
            return new_state
            
        except Exception as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="GENERATE_FAILED",
                error_message=str(e)
            )
            raise
    
    async def persist_asset_node(self, state: ImageAgentState) -> ImageAgentState:
        """
        Persist Asset Node: Save image metadata to database.
        
        Saves the generated image artifact to the video_assets table
        and emits the final result via Socket.io.
        
        Args:
            state: Current workflow state with image_url
            
        Returns:
            Updated state with asset_id
        """
        from app.application.agents.prompts import IMAGE_PROMPTS
        from app.infrastructure.database import get_session
        from app.infrastructure.repositories.video_asset_repository import VideoAssetRepository
        
        workflow_id = state["workflow_id"]
        
        # Update workflow state
        _workflow_states[workflow_id]["current_stage"] = "persist_asset"
        
        # Emit thought event
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=IMAGE_PROMPTS.persist_start,
            node_name="persist_asset"
        )
        
        try:
            # Get artifact from workflow state
            artifact = _workflow_states[workflow_id].get("artifact")
            
            if artifact is None:
                raise ValueError("No artifact found in workflow state")
            
            # Persist to database
            async for session in get_session():
                repo = VideoAssetRepository(session)
                saved_artifact = await repo.create(artifact)
                await session.commit()
                asset_id = str(saved_artifact.id)
                break
            
            # Emit completion thought
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=IMAGE_PROMPTS.persist_complete,
                node_name="persist_asset"
            )
            
            # Emit final result
            await socket_manager.emit_result(
                workflow_id=workflow_id,
                result_data={
                    "imageUrl": state["image_url"],
                    "assetId": asset_id,
                    "optimizedPrompt": state["optimized_prompt"],
                    "stage": "completed"
                }
            )
            
            new_state = {
                **state,
                "asset_id": asset_id,
                "current_stage": "completed",
            }
            
            # Update workflow state to completed
            _workflow_states[workflow_id] = {
                "status": "completed",
                "current_stage": "completed",
                "state": new_state,
            }
            
            logger.info(f"Image persisted for workflow {workflow_id}, asset_id: {asset_id}")
            return new_state
            
        except Exception as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="PERSIST_FAILED",
                error_message=str(e)
            )
            raise
    
    # =========================================================================
    # Run methods
    # =========================================================================
    
    async def run(
        self,
        prompt: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        workflow_id: Optional[str] = None,
    ) -> ImageAgentState:
        """
        Execute the complete image generation workflow using LangGraph.
        
        Args:
            prompt: Text description of the image to generate
            width: Image width in pixels
            height: Image height in pixels
            workflow_id: Optional workflow ID (generated if not provided)
            
        Returns:
            Final workflow state with generated image details
        """
        workflow_id = workflow_id or str(uuid.uuid4())
        
        # Initialize state
        initial_state: ImageAgentState = {
            "prompt": prompt,
            "optimized_prompt": "",
            "workflow_id": workflow_id,
            "current_stage": None,
            "image_url": "",
            "asset_id": None,
            "width": width,
            "height": height,
            "error": None,
        }
        
        logger.info(f"Starting image generation workflow: {workflow_id}")
        
        # Execute workflow using LangGraph with thread_id for checkpointing
        config = {"configurable": {"thread_id": workflow_id}}
        result = await self._graph.ainvoke(initial_state, config)
        
        logger.info(f"Image generation workflow completed: {workflow_id}")
        
        return result
    
    async def run_async(
        self,
        prompt: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        workflow_id: Optional[str] = None,
    ) -> str:
        """
        Start workflow asynchronously and return workflow_id immediately.
        
        This method is used by API endpoints to return quickly while
        the workflow runs in the background.
        
        Args:
            prompt: Text description of the image to generate
            width: Image width in pixels
            height: Image height in pixels
            workflow_id: Optional workflow ID (generated if not provided)
            
        Returns:
            workflow_id for tracking
        """
        workflow_id = workflow_id or str(uuid.uuid4())
        
        # Create background task
        task = asyncio.create_task(
            self._run_with_error_handling(
                prompt=prompt,
                width=width,
                height=height,
                workflow_id=workflow_id,
            )
        )
        
        # Store task for cancellation support
        _workflow_tasks[workflow_id] = task
        
        return workflow_id
    
    async def _run_with_error_handling(
        self,
        prompt: str,
        width: int,
        height: int,
        workflow_id: str,
    ) -> None:
        """Run workflow with error handling for background execution."""
        try:
            await self.run(
                prompt=prompt,
                width=width,
                height=height,
                workflow_id=workflow_id,
            )
        except asyncio.CancelledError:
            logger.info(f"Workflow {workflow_id} was cancelled")
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="WORKFLOW_CANCELLED",
                error_message="Workflow was cancelled by user"
            )
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            if workflow_id in _workflow_states:
                _workflow_states[workflow_id]["status"] = "failed"
                _workflow_states[workflow_id]["error"] = str(e)
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="WORKFLOW_FAILED",
                error_message=str(e)
            )
        finally:
            # Clean up task reference
            _workflow_tasks.pop(workflow_id, None)

