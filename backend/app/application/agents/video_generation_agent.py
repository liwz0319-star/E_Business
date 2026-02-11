"""
Video Generation Agent

Generates product videos with automatic slideshow fallback.
"""

import logging
from typing import Dict, Any, List
from uuid import UUID

from app.application.tools import ToolRegistry

logger = logging.getLogger(__name__)


class VideoGenerationAgent:
    """
    Agent for generating product videos.

    Strategy:
    1. Try primary video generation (e.g., Runway, Pika)
    2. On timeout (30s) or error, fallback to slideshow
    3. Always returns a valid video asset
    """

    def __init__(self, tools: ToolRegistry):
        """
        Initialize video generation agent.

        Args:
            tools: ToolRegistry instance
        """
        self.tools = tools

    async def run(
        self,
        analysis: Dict[str, Any],
        image_assets: List[Dict[str, Any]],
        request: Dict[str, Any],
        workspace: str,
    ) -> Dict[str, Any]:
        """
        Generate video for product.

        Args:
            analysis: Product analysis data
            image_assets: List of generated image assets
            request: Original request dict with options
            workspace: Workspace directory path

        Returns:
            Video asset dict:
            {
                "asset_id": str,
                "asset_type": "video",
                "url": str,
                "is_fallback": bool,
                "provider": str
            }
        """
        logger.info(f"Starting video generation for workspace: {workspace}")

        try:
            # Build video prompt
            prompt = self._build_video_prompt(analysis, request.get("background", ""))
            logger.info(f"Video prompt: {prompt[:100]}...")

            # Extract image URLs
            image_urls = [asset.get("url", "") for asset in image_assets]
            logger.info(f"Using {len(image_urls)} images for video")

            # Get video duration from options
            options = request.get("options", {})
            duration = options.get("video_duration_sec", 15)
            logger.info(f"Target duration: {duration}s")

            # Generate video (with automatic fallback)
            video_artifact = await self.tools.video.generate_video(
                prompt=prompt,
                image_paths=image_urls,
                duration_sec=duration,
                timeout_sec=30,
            )

            logger.info(
                f"Video generated via {video_artifact.get('provider', 'unknown')} "
                f"(fallback: {video_artifact.get('is_fallback', False)})"
            )

            # Save asset to database
            user_id = request.get("user_id")
            workflow_id = request.get("workflow_id")

            if user_id and workflow_id:
                saved_asset = await self.tools.video.save_asset(
                    artifact=video_artifact,
                    user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                    workflow_id=workflow_id,
                )

                # Save metadata to workspace
                self._save_video_metadata(saved_asset, workspace)

                return saved_asset
            else:
                # Return unsaved artifact
                return video_artifact

        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Video generation failed: {str(e)}")

    def _build_video_prompt(
        self,
        analysis: Dict[str, Any],
        background: str,
    ) -> str:
        """
        Build video generation prompt.

        Args:
            analysis: Product analysis
            background: User context

        Returns:
            Video prompt string
        """
        category = analysis.get("category", "product")
        style = analysis.get("style", "modern")
        features = analysis.get("key_features", [])

        prompt = f"""
Create a dynamic product video for a {category}.

Style: {style}
Key Features: {', '.join(features[:3])}

Context: {background}

Requirements:
- Smooth transitions between product shots
- Highlight key features dynamically
- Professional, commercial quality
- Engaging visual narrative
- Showcase product from multiple angles
"""

        return prompt.strip()

    def _save_video_metadata(
        self,
        asset: Dict[str, Any],
        workspace: str,
    ) -> None:
        """
        Save video metadata to workspace.

        Args:
            asset: Video asset dict
            workspace: Workspace path
        """
        import json

        metadata_path = f"{workspace}/artifacts/video/metadata.json"
        self.tools.filesystem.write_json(metadata_path, asset)
        logger.info(f"Video metadata saved to: {metadata_path}")
