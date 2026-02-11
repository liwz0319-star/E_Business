"""
Subagents

Wrapper adapters for existing CopywritingAgent and ImageAgent.
"""

import logging
from typing import Dict, Any
from uuid import UUID

from app.application.agents.copywriting_agent import CopywritingAgent
from app.application.agents.image_agent import ImageAgent

logger = logging.getLogger(__name__)


class CopywritingSubagent:
    """
    Adapter for CopywritingAgent to work with DeepOrchestrator.

    Wraps the existing CopywritingAgent to provide a simplified interface.
    """

    def __init__(self, agent: CopywritingAgent, tools):
        """
        Initialize copywriting subagent.

        Args:
            agent: Existing CopywritingAgent instance
            tools: ToolRegistry for file operations
        """
        self.agent = agent
        self.tools = tools

    async def run(
        self,
        analysis: Dict[str, Any],
        request: Dict[str, Any],
        workspace: str,
    ) -> list[Dict[str, Any]]:
        """
        Generate copywriting for product.

        Args:
            analysis: Product analysis data
            request: Original request dict
            workspace: Workspace directory path

        Returns:
            List of copywriting assets:
            [
                {
                    "channel": "product_page",
                    "path": "...",
                    "content": "...",
                    "asset_id": "..."
                },
                ...
            ]
        """
        logger.info("Running copywriting subagent")

        try:
            # Extract product info from analysis
            product_name = analysis.get("category", "Product")
            features = analysis.get("key_features", [])

            # Run existing copywriting agent
            result = await self.agent.run(
                product_name=product_name,
                features=features,
                brand_guidelines=request.get("background", ""),
            )

            # Save each output variant
            outputs = []
            channels = ["product_page", "social_post", "ad_short"]

            for i, channel in enumerate(channels):
                # Get content from result
                content = result.get("final_copy", "")

                # Generate path
                path = f"{workspace}/artifacts/copy/{channel}_v1.md"

                # Save to file
                self.tools.filesystem.write_file(path, content)

                outputs.append({
                    "channel": channel,
                    "path": path,
                    "content": content,
                    "asset_id": f"copy_{i}",
                })

            logger.info(f"Generated {len(outputs)} copywriting assets")
            return outputs

        except Exception as e:
            logger.error(f"Copywriting failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Copywriting failed: {str(e)}")


class ImageSubagent:
    """
    Adapter for ImageAgent to work with DeepOrchestrator.

    Wraps the existing ImageAgent to provide a simplified interface.
    """

    def __init__(self, agent: ImageAgent, tools):
        """
        Initialize image subagent.

        Args:
            agent: Existing ImageAgent instance
            tools: ToolRegistry for image operations
        """
        self.agent = agent
        self.tools = tools

    async def run(
        self,
        analysis: Dict[str, Any],
        request: Dict[str, Any],
        workspace: str,
    ) -> list[Dict[str, Any]]:
        """
        Generate images for product.

        Args:
            analysis: Product analysis data
            request: Original request dict
            workspace: Workspace directory path

        Returns:
            List of image assets:
            [
                {
                    "scene": "hero",
                    "url": "https://...",
                    "asset_id": "uuid",
                    "label": "hero"
                },
                ...
            ]
        """
        logger.info("Running image subagent")

        try:
            # Get scenes from analysis
            scenes = analysis.get("suggested_scenes", ["hero", "lifestyle", "detail"])
            options = request.get("options", {})
            num_variants = min(options.get("image_variants", 3), len(scenes))

            results = []

            for i, scene in enumerate(scenes[:num_variants]):
                # Build prompt for this scene
                prompt = self.tools.vision.build_image_generation_prompt(
                    scene=scene,
                    analysis=analysis,
                    background=request.get("background", ""),
                )

                # Generate image
                artifact = await self.tools.image.generate_image(
                    prompt=prompt,
                    width=1024,
                    height=1024,
                )

                # Save asset
                user_id = request.get("user_id")
                workflow_id = request.get("workflow_id")

                if user_id and workflow_id:
                    saved = await self.tools.image.save_asset(
                        artifact=artifact,
                        user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                        workflow_id=workflow_id,
                        label=scene,
                    )

                    results.append({
                        "scene": scene,
                        **saved,
                    })

            logger.info(f"Generated {len(results)} image assets")
            return results

        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Image generation failed: {str(e)}")
