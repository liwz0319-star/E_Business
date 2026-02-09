"""
Copywriting Agent using LangGraph workflow.

Implements a multi-stage workflow for generating product marketing copy:
Plan -> Draft -> Critique -> Finalize
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict
from typing import Any, Dict, Optional, TypedDict, List

from app.core.config import get_settings

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.factory import ProviderFactory
from app.domain.entities.generation import GenerationRequest, StreamChunk
from app.domain.entities.agent_state import (
    CopywritingState,
    CopywritingStage,
)
from app.domain.exceptions import HTTPClientError
from app.interface.ws.socket_manager import socket_manager

try:
    from app.application.agents.prompts import COPYWRITING_PROMPTS
except ImportError:
    # Fallback: prompts module not found - use minimal defaults
    logger = logging.getLogger(__name__)
    logger.warning("prompts module not found, using minimal defaults")
    
    class _DefaultPrompts:
        plan_start = "Analyzing product: {product_name}..."
        plan_complete = "Plan created."
        draft_start = "Drafting copy..."
        draft_complete = "Draft created."
        critique_start = "Reviewing draft..."
        critique_complete = "Critique done."
        finalize_start = "Polishing copy..."
        finalize_complete = "Final copy ready."
        
        @staticmethod
        def get_plan_prompt(product_name: str, features: list, brand_guidelines: str = "") -> str:
            return f"Create marketing plan for {product_name} with features: {', '.join(features)}"
        
        @staticmethod
        def get_draft_prompt(product_name: str, plan: str) -> str:
            return f"Create draft for {product_name} based on plan: {plan}"
        
        @staticmethod
        def get_critique_prompt(draft: str) -> str:
            return f"Critique this draft: {draft}"
        
        @staticmethod
        def get_finalize_prompt(draft: str, critique: str) -> str:
            return f"Finalize based on draft: {draft} and critique: {critique}"
    
    COPYWRITING_PROMPTS = _DefaultPrompts()

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """TypedDict for LangGraph state."""
    product_name: str
    features: List[str]
    workflow_id: str
    current_stage: Optional[str]
    plan: Optional[str]
    draft: Optional[str]
    critique: Optional[str]
    final_copy: Optional[str]
    brand_guidelines: Optional[str]


# Workflow state storage for status queries and cancellation
_workflow_states: Dict[str, Dict[str, Any]] = {}
_workflow_tasks: Dict[str, asyncio.Task] = {}
_workflow_states_lock: asyncio.Lock = asyncio.Lock()


class CopywritingAgent:
    """
    AI agent for generating product marketing copy using LangGraph.
    
    Workflow stages:
    1. Plan - Analyze product and create marketing outline
    2. Draft - Generate initial copy based on plan
    3. Critique - Self-review and suggest improvements
    4. Finalize - Produce polished final copy
    
    Usage:
        agent = CopywritingAgent()
        result = await agent.run(
            product_name="Smart Watch",
            features=["GPS", "Heart Monitor"]
        )
    """
    
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2000
    
    # Class-level rate limiting for error logs with thread-safe access
    _error_log_times: Dict[str, float] = defaultdict(float)
    _error_log_lock: asyncio.Lock = asyncio.Lock()
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        """
        Initialize the copywriting agent.
        
        Args:
            model: LLM model to use
            temperature: Generation temperature
            max_tokens: Max tokens per generation
        """
        self.model = model or self.DEFAULT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._checkpointer = MemorySaver()
        self._graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        workflow = StateGraph(GraphState)
        
        # Add nodes (using _step suffix to avoid conflict with state keys)
        workflow.add_node("plan_step", self.plan_node)
        workflow.add_node("draft_step", self.draft_node)
        workflow.add_node("critique_step", self.critique_node)
        workflow.add_node("finalize_step", self.finalize_node)
        
        # Set entry point
        workflow.set_entry_point("plan_step")
        
        # Add edges: Plan -> Draft -> Critique -> Finalize -> END
        workflow.add_edge("plan_step", "draft_step")
        workflow.add_edge("draft_step", "critique_step")
        workflow.add_edge("critique_step", "finalize_step")
        workflow.add_edge("finalize_step", END)
        
        # Compile with checkpointer for state persistence (fixes issue #5)
        return workflow.compile(checkpointer=self._checkpointer)
    
    @classmethod
    async def _should_log_error(cls, error_key: str) -> bool:
        """Check if enough time has passed since last error log (thread-safe)."""
        async with cls._error_log_lock:
            now = time.time()
            settings = get_settings()  # CRITICAL FIX: Call get_settings() dynamically
            cooldown = settings.error_log_cooldown_seconds
            if now - cls._error_log_times[error_key] > cooldown:
                cls._error_log_times[error_key] = now
                return True
            return False
    
    @classmethod
    def get_workflow_status(cls, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: Workflow ID to query
            
        Returns:
            Workflow state dict or None if not found
        """
        return _workflow_states.get(workflow_id)
    
    @classmethod
    def cancel_workflow(cls, workflow_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: Workflow ID to cancel
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        task = _workflow_tasks.get(workflow_id)
        if task and not task.done():
            task.cancel()
            if workflow_id in _workflow_states:
                _workflow_states[workflow_id]["status"] = "cancelled"
            return True
        return False
    
    async def _generate(
        self,
        prompt: str,
        workflow_id: str,
    ) -> str:
        """
        Generate text using the DeepSeek provider.

        Args:
            prompt: Prompt for generation
            workflow_id: Workflow ID for error reporting

        Returns:
            Generated text content

        Raises:
            HTTPClientError: On generation failure
        """
        generator = ProviderFactory.get_provider("deepseek")
        async with generator:
            response = await generator.generate(
                GenerationRequest(
                    prompt=prompt,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
            )
            return response.content

    async def _generate_with_streaming(
        self,
        prompt: str,
        workflow_id: str,
        node_name: str,
    ) -> str:
        """
        Generate text with streaming callback for real-time thought updates.

        Emits reasoning_content in real-time as the AI "thinks".

        IMPORTANT: Falls back to non-streaming mode if streaming fails,
        with a warning log. This ensures resilience even if streaming
        is temporarily unavailable.

        Args:
            prompt: Prompt for generation
            workflow_id: Workflow ID for event correlation
            node_name: Name of the current node (e.g., "plan", "draft")

        Returns:
            Generated text content

        Raises:
            HTTPClientError: On generation failure (even fallback fails)
        """
        async def stream_callback(chunk: StreamChunk) -> None:
            """Callback for streaming chunks."""
            try:
                # Emit reasoning content if available
                if chunk.reasoning_content:
                    await socket_manager.emit_thought(
                        workflow_id=workflow_id,
                        content=chunk.reasoning_content,
                        node_name=node_name
                    )
            except Exception as e:
                # Rate-limited logging to prevent log flooding
                error_key = f"emit_thought_{workflow_id}_{node_name}"
                if await CopywritingAgent._should_log_error(error_key):
                    settings = get_settings()  # CRITICAL FIX: Call get_settings() dynamically
                    cooldown = settings.error_log_cooldown_seconds
                    logger.warning(
                        f"Failed to emit thought for {node_name} (will suppress similar errors for {cooldown}s): {e}"
                    )

        try:
            # Emit tool_call event before DeepSeek API call (fixes issue #7)
            await socket_manager.emit_tool_call(
                workflow_id=workflow_id,
                tool_name="deepseek_generate",
                status="in_progress",
                message=f"Calling DeepSeek API for {node_name}"
            )
            
            generator = ProviderFactory.get_provider("deepseek")
            async with generator:
                response = await generator.generate_stream_with_callback(
                    request=GenerationRequest(
                        prompt=prompt,
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    ),
                    callback=stream_callback,
                )
                
                # Emit completion event
                await socket_manager.emit_tool_call(
                    workflow_id=workflow_id,
                    tool_name="deepseek_generate",
                    status="completed",
                    message=f"DeepSeek API call completed for {node_name}"
                )
                
                return response.content
        except Exception as e:
            # Emit error event
            await socket_manager.emit_tool_call(
                workflow_id=workflow_id,
                tool_name="deepseek_generate",
                status="error",
                message=f"DeepSeek API call failed: {str(e)}"
            )
            # Fallback to non-streaming if streaming fails
            logger.warning(f"Streaming failed for {node_name}, falling back to regular generation: {e}")
            return await self._generate(prompt, workflow_id)
    
    async def plan_node(self, state: GraphState) -> GraphState:
        """
        Plan node: Create marketing outline for the product.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with plan
        """
        workflow_id = state["workflow_id"]
        product_name = state["product_name"]
        features = state["features"]
        brand_guidelines = state.get("brand_guidelines") or ""
        
        # Update workflow state
        _workflow_states[workflow_id] = {
            "status": "running",
            "current_stage": "plan",
            "state": state,
        }
        
        # Emit thought event using prompt template
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=COPYWRITING_PROMPTS.plan_start.format(product_name=product_name),
            node_name="plan"
        )
        
        # Use prompt template (fixes issue #6)
        prompt = COPYWRITING_PROMPTS.get_plan_prompt(
            product_name=product_name,
            features=features,
            brand_guidelines=brand_guidelines,
        )
        
        try:
            # Use streaming generation to stream DeepSeek reasoning
            plan = await self._generate_with_streaming(prompt, workflow_id, "plan")
            
            # Emit completion thought using prompt template
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=COPYWRITING_PROMPTS.plan_complete,
                node_name="plan"
            )
            
            new_state = {
                **state,
                "plan": plan,
                "current_stage": CopywritingStage.PLAN.value,
            }
            _workflow_states[workflow_id]["state"] = new_state
            return new_state
        except HTTPClientError as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="PLAN_FAILED",
                error_message=str(e)
            )
            raise
    
    async def draft_node(self, state: GraphState) -> GraphState:
        """
        Draft node: Generate initial marketing copy.
        
        Args:
            state: Current workflow state with plan
            
        Returns:
            Updated state with draft
        """
        workflow_id = state["workflow_id"]
        product_name = state["product_name"]
        plan = state.get("plan", "")
        
        # Update workflow state
        _workflow_states[workflow_id]["current_stage"] = "draft"
        
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=COPYWRITING_PROMPTS.draft_start,
            node_name="draft"
        )
        
        # Use prompt template (fixes issue #6)
        prompt = COPYWRITING_PROMPTS.get_draft_prompt(
            product_name=product_name,
            plan=plan,
        )
        
        try:
            # Use streaming generation to stream DeepSeek reasoning
            draft = await self._generate_with_streaming(prompt, workflow_id, "draft")
            
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=COPYWRITING_PROMPTS.draft_complete,
                node_name="draft"
            )
            
            new_state = {
                **state,
                "draft": draft,
                "current_stage": CopywritingStage.DRAFT.value,
            }
            _workflow_states[workflow_id]["state"] = new_state
            return new_state
        except HTTPClientError as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="DRAFT_FAILED",
                error_message=str(e)
            )
            raise
    
    async def critique_node(self, state: GraphState) -> GraphState:
        """
        Critique node: Review draft and suggest improvements.
        
        Args:
            state: Current workflow state with draft
            
        Returns:
            Updated state with critique
        """
        workflow_id = state["workflow_id"]
        draft = state.get("draft", "")
        
        # Update workflow state
        _workflow_states[workflow_id]["current_stage"] = "critique"
        
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=COPYWRITING_PROMPTS.critique_start,
            node_name="critique"
        )
        
        # Use prompt template (fixes issue #6)
        prompt = COPYWRITING_PROMPTS.get_critique_prompt(draft=draft)
        
        try:
            # Use streaming generation to stream DeepSeek reasoning
            critique = await self._generate_with_streaming(prompt, workflow_id, "critique")
            
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=COPYWRITING_PROMPTS.critique_complete,
                node_name="critique"
            )
            
            new_state = {
                **state,
                "critique": critique,
                "current_stage": CopywritingStage.CRITIQUE.value,
            }
            _workflow_states[workflow_id]["state"] = new_state
            return new_state
        except HTTPClientError as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="CRITIQUE_FAILED",
                error_message=str(e)
            )
            raise
    
    async def finalize_node(self, state: GraphState) -> GraphState:
        """
        Finalize node: Produce polished final copy.
        
        Args:
            state: Current workflow state with draft and critique
            
        Returns:
            Updated state with final_copy
        """
        workflow_id = state["workflow_id"]
        draft = state.get("draft", "")
        critique = state.get("critique", "")
        
        # Update workflow state
        _workflow_states[workflow_id]["current_stage"] = "finalize"
        
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=COPYWRITING_PROMPTS.finalize_start,
            node_name="finalize"
        )
        
        # Use prompt template (fixes issue #6)
        prompt = COPYWRITING_PROMPTS.get_finalize_prompt(
            draft=draft,
            critique=critique,
        )
        
        try:
            # Use streaming generation to stream DeepSeek reasoning
            final_copy = await self._generate_with_streaming(prompt, workflow_id, "finalize")
            
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=COPYWRITING_PROMPTS.finalize_complete,
                node_name="finalize"
            )
            
            # Emit final result
            await socket_manager.emit_result(
                workflow_id=workflow_id,
                result_data={
                    "finalCopy": final_copy,
                    "stage": "completed"
                }
            )
            
            new_state = {
                **state,
                "final_copy": final_copy,
                "current_stage": CopywritingStage.COMPLETED.value,
            }
            
            # Update workflow state to completed
            _workflow_states[workflow_id] = {
                "status": "completed",
                "current_stage": "completed",
                "state": new_state,
            }
            
            return new_state
        except HTTPClientError as e:
            await socket_manager.emit_error(
                workflow_id=workflow_id,
                error_code="FINALIZE_FAILED",
                error_message=str(e)
            )
            raise
    
    async def run(
        self,
        product_name: str,
        features: List[str],
        brand_guidelines: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> GraphState:
        """
        Execute the complete copywriting workflow using LangGraph.
        
        Args:
            product_name: Product name
            features: List of product features
            brand_guidelines: Optional brand voice guidelines
            workflow_id: Optional workflow ID (generated if not provided)
            
        Returns:
            Final workflow state with all generated content
        """
        workflow_id = workflow_id or str(uuid.uuid4())
        
        # Initialize state
        initial_state: GraphState = {
            "product_name": product_name,
            "features": features,
            "workflow_id": workflow_id,
            "current_stage": None,
            "plan": None,
            "draft": None,
            "critique": None,
            "final_copy": None,
            "brand_guidelines": brand_guidelines,
        }
        
        logger.info(f"Starting copywriting workflow: {workflow_id}")
        
        # Execute workflow using LangGraph with thread_id for checkpointing
        config = {"configurable": {"thread_id": workflow_id}}
        result = await self._graph.ainvoke(initial_state, config)
        
        logger.info(f"Copywriting workflow completed: {workflow_id}")
        
        return result
    
    async def run_async(
        self,
        product_name: str,
        features: List[str],
        brand_guidelines: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> str:
        """
        Start workflow asynchronously and return workflow_id immediately.
        
        This method is used by API endpoints to return quickly while
        the workflow runs in the background.
        
        Args:
            product_name: Product name
            features: List of product features
            brand_guidelines: Optional brand voice guidelines
            workflow_id: Optional workflow ID (generated if not provided)
            
        Returns:
            workflow_id for tracking
        """
        workflow_id = workflow_id or str(uuid.uuid4())
        
        # Create background task
        task = asyncio.create_task(
            self._run_with_error_handling(
                product_name=product_name,
                features=features,
                brand_guidelines=brand_guidelines,
                workflow_id=workflow_id,
            )
        )
        
        # Store task for cancellation support
        _workflow_tasks[workflow_id] = task
        
        return workflow_id
    
    async def _run_with_error_handling(
        self,
        product_name: str,
        features: List[str],
        brand_guidelines: Optional[str],
        workflow_id: str,
    ) -> None:
        """Run workflow with error handling for background execution."""
        try:
            await self.run(
                product_name=product_name,
                features=features,
                brand_guidelines=brand_guidelines,
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

