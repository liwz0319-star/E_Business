"""
Product Analysis Agent

Analyzes product images and context to extract key information for content generation.
"""

import logging
from typing import Dict, Any
from uuid import UUID

from app.application.tools import ToolRegistry

logger = logging.getLogger(__name__)


class ProductAnalysisAgent:
    """
    Agent for analyzing product images and context.

    Extracts:
    - Product category and style
    - Key features and materials
    - Target audience
    - Suggested marketing angles
    """

    def __init__(self, tools: ToolRegistry):
        """
        Initialize product analysis agent.

        Args:
            tools: ToolRegistry instance
        """
        self.tools = tools

    async def run(
        self,
        request: Dict[str, Any],
        workspace: str,
    ) -> Dict[str, Any]:
        """
        Analyze product and generate analysis report.

        Args:
            request: Request dict with:
            {
                "image_url": str | None,
                "image_asset_id": UUID | None,
                "background": str,
                "user_id": UUID
            }
            workspace: Workspace directory path

        Returns:
            Analysis dict:
            {
                "category": str,
                "style": str,
                "materials": List[str],
                "key_features": List[str],
                "suggested_scenes": List[str],
                "color_palette": List[str],
                "target_audience": str,
                "price_range": str,
                "keywords": List[str],
                "marketing_angles": List[str]
            }
        """
        logger.info(f"Starting product analysis for workspace: {workspace}")

        try:
            # Resolve input image
            image_source = self._resolve_input_image(request)
            logger.info(f"Analyzing image: {image_source}")

            # Analyze image using vision tools
            analysis = await self.tools.vision.analyze_product_image(image_source)
            logger.info(f"Vision analysis complete: {analysis.get('category', 'unknown')}")

            # Enhance with background context
            enhanced_analysis = await self._enhance_with_context(
                analysis,
                request.get("background", ""),
            )

            # Save analysis report to workspace
            report_path = f"{workspace}/workspace/analysis_report.md"
            self._save_analysis_report(enhanced_analysis, report_path)
            logger.info(f"Analysis report saved to: {report_path}")

            return enhanced_analysis

        except Exception as e:
            logger.error(f"Product analysis failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Product analysis failed: {str(e)}")

    def _resolve_input_image(self, request: Dict[str, Any]) -> str:
        """
        Resolve input image URL or asset ID.

        Args:
            request: Request dict

        Returns:
            Image URL string

        Raises:
            ValueError: If neither image_url nor image_asset_id provided
        """
        image_url = request.get("image_url")
        image_asset_id = request.get("image_asset_id")

        if image_url:
            return image_url

        if image_asset_id:
            # TODO: Fetch asset URL from database
            # For now, return placeholder
            return f"asset://{image_asset_id}"

        raise ValueError("Either image_url or image_asset_id is required")

    async def _enhance_with_context(
        self,
        base_analysis: Dict[str, Any],
        background: str,
    ) -> Dict[str, Any]:
        """
        Enhance base analysis with user-provided context.

        Args:
            base_analysis: Initial vision analysis
            background: User context

        Returns:
            Enhanced analysis dict
        """
        if not background:
            return base_analysis

        try:
            # Use text tools to extract additional insights
            prompt = f"""
Based on this product analysis and user background, suggest 3-5 marketing angles:

Product Analysis:
{base_analysis}

User Background:
{background}

Output as JSON array of marketing angle strings.
"""

            # This is a simplified version - in production you'd parse the LLM response
            marketing_angles = [
                f"Premium quality {base_analysis.get('category', 'product')}",
                f"Modern {base_analysis.get('style', 'design')} aesthetic",
                f"Targeted at {base_analysis.get('target_audience', 'general audience')}",
            ]

            base_analysis["marketing_angles"] = marketing_angles
            return base_analysis

        except Exception as e:
            logger.warning(f"Context enhancement failed: {str(e)}")
            return base_analysis

    def _save_analysis_report(
        self,
        analysis: Dict[str, Any],
        report_path: str,
    ) -> None:
        """
        Save analysis as markdown report.

        Args:
            analysis: Analysis dict
            report_path: Output file path
        """
        import json

        markdown = f"""# Product Analysis Report

## Category & Style
- **Category**: {analysis.get('category', 'unknown')}
- **Style**: {analysis.get('style', 'unknown')}

## Materials
{', '.join(analysis.get('materials', []))}

## Key Features
{chr(10).join(f"- {f}" for f in analysis.get('key_features', []))}

## Suggested Scenes
{', '.join(analysis.get('suggested_scenes', []))}

## Color Palette
{', '.join(analysis.get('color_palette', []))}

## Target Audience
{analysis.get('target_audience', 'unknown')}

## Price Range
{analysis.get('price_range', 'unknown')}

## Keywords
{', '.join(analysis.get('keywords', []))}

## Marketing Angles
{chr(10).join(f"- {a}" for a in analysis.get('marketing_angles', []))}

---

## Raw Data
```json
{json.dumps(analysis, indent=2, ensure_ascii=False)}
```
"""

        self.tools.filesystem.write_file(report_path, markdown)
