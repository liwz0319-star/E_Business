"""
QA Agent

Performs quality assurance checks on generated content.
"""

import logging
from typing import Dict, Any, List
from uuid import UUID

from app.application.tools import ToolRegistry

logger = logging.getLogger(__name__)


class QAAgent:
    """
    Agent for quality assurance of generated content.

    Checks:
    - Copywriting quality and coherence
    - Image relevance and quality
    - Video completeness
    - Overall package consistency
    """

    def __init__(self, tools: ToolRegistry):
        """
        Initialize QA agent.

        Args:
            tools: ToolRegistry instance
        """
        self.tools = tools

    async def run(
        self,
        analysis: Dict[str, Any],
        copy_assets: List[Dict[str, Any]],
        image_assets: List[Dict[str, Any]],
        video_asset: Dict[str, Any],
        workspace: str,
    ) -> Dict[str, Any]:
        """
        Perform QA checks on generated content.

        Args:
            analysis: Product analysis data
            copy_assets: List of generated copywriting assets
            image_assets: List of generated image assets
            video_asset: Generated video asset
            workspace: Workspace directory path

        Returns:
            QA report dict:
            {
                "score": float,  # 0.0 to 1.0
                "passed": bool,
                "checks": {
                    "copywriting": {"score": float, "issues": List[str]},
                    "images": {"score": float, "issues": List[str]},
                    "video": {"score": float, "issues": List[str]},
                    "consistency": {"score": float, "issues": List[str]}
                },
                "issues": List[str],
                "suggestions": List[str]
            }
        """
        logger.info(f"Starting QA checks for workspace: {workspace}")

        try:
            # Run individual checks
            copywriting_check = self._check_copywriting(copy_assets, analysis)
            images_check = self._check_images(image_assets, analysis)
            video_check = self._check_video(video_asset)
            consistency_check = self._check_consistency(
                copy_assets, image_assets, video_asset, analysis
            )

            # Calculate overall score
            checks = {
                "copywriting": copywriting_check,
                "images": images_check,
                "video": video_check,
                "consistency": consistency_check,
            }

            overall_score = self._calculate_overall_score(checks)
            passed = overall_score >= 0.7  # 70% threshold

            # Aggregate issues and suggestions
            all_issues = []
            all_suggestions = []

            for check_name, check in checks.items():
                all_issues.extend(check.get("issues", []))
                all_suggestions.extend(check.get("suggestions", []))

            report = {
                "score": overall_score,
                "passed": passed,
                "checks": checks,
                "issues": all_issues,
                "suggestions": all_suggestions,
            }

            # Save report to workspace
            report_path = f"{workspace}/workspace/qa_report.md"
            self._save_qa_report(report, report_path)
            logger.info(f"QA report saved: score={overall_score:.2f}, passed={passed}")

            return report

        except Exception as e:
            logger.error(f"QA check failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"QA check failed: {str(e)}")

    def _check_copywriting(
        self,
        copy_assets: List[Dict[str, Any]],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check copywriting quality."""
        issues = []
        suggestions = []
        score = 1.0

        # Check if we have copywriting assets
        if not copy_assets:
            issues.append("No copywriting generated")
            score = 0.0
            return {"score": score, "issues": issues, "suggestions": suggestions}

        # Check for required channels
        channels = {asset.get("channel") for asset in copy_assets}
        required_channels = {"product_page", "social_post", "ad_short"}
        missing = required_channels - channels

        if missing:
            issues.append(f"Missing copywriting channels: {', '.join(missing)}")
            score -= 0.3 * len(missing)

        # Check content length
        for asset in copy_assets:
            content = asset.get("content", "")
            if len(content) < 50:
                issues.append(f"Copy for {asset.get('channel')} is too short")
                score -= 0.2

        if score < 0:
            score = 0

        suggestions.append("Consider A/B testing different copy variations")

        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_images(
        self,
        image_assets: List[Dict[str, Any]],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check image quality and relevance."""
        issues = []
        suggestions = []
        score = 1.0

        if not image_assets:
            issues.append("No images generated")
            return {"score": 0.0, "issues": issues, "suggestions": suggestions}

        # Check for required scenes
        scenes = {asset.get("label") for asset in image_assets}
        suggested_scenes = set(analysis.get("suggested_scenes", ["hero", "lifestyle", "detail"]))
        missing = suggested_scenes - scenes

        if missing:
            issues.append(f"Missing image scenes: {', '.join(missing)}")
            score -= 0.2 * len(missing)

        # Check image count
        if len(image_assets) < 3:
            issues.append("Insufficient number of images")
            score -= 0.3

        if score < 0:
            score = 0

        suggestions.append("Ensure images match brand color palette")

        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_video(
        self,
        video_asset: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check video quality."""
        issues = []
        suggestions = []
        score = 1.0

        if not video_asset:
            issues.append("No video generated")
            return {"score": 0.0, "issues": issues, "suggestions": suggestions}

        # Check if fallback was used
        is_fallback = video_asset.get("is_fallback", False)
        if is_fallback:
            issues.append("Video generation used fallback (slideshow)")
            score -= 0.3
            suggestions.append("Consider improving product images for better video generation")

        # Check video URL
        if not video_asset.get("url"):
            issues.append("Video URL missing")
            score = 0.0

        if score < 0:
            score = 0

        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_consistency(
        self,
        copy_assets: List[Dict[str, Any]],
        image_assets: List[Dict[str, Any]],
        video_asset: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check overall consistency across assets."""
        issues = []
        suggestions = []
        score = 1.0

        # Check if all assets reference the same product
        if not copy_assets or not image_assets or not video_asset:
            issues.append("Missing assets for consistency check")
            score -= 0.5

        # Check if messaging is aligned
        keywords = analysis.get("keywords", [])
        if not keywords:
            issues.append("No keywords found in analysis for consistency check")
            score -= 0.2

        suggestions.append("Review all assets for brand voice consistency")

        if score < 0:
            score = 0

        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _calculate_overall_score(self, checks: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall QA score."""
        weights = {
            "copywriting": 0.3,
            "images": 0.3,
            "video": 0.2,
            "consistency": 0.2,
        }

        total = 0.0
        for check_name, weight in weights.items():
            check_score = checks.get(check_name, {}).get("score", 0.0)
            total += check_score * weight

        return round(total, 2)

    def _save_qa_report(
        self,
        report: Dict[str, Any],
        report_path: str,
    ) -> None:
        """Save QA report as markdown."""
        import json

        markdown = f"""# QA Report

## Overall Score: {report['score']:.2f}
**Status**: {'✓ PASSED' if report['passed'] else '✗ FAILED'}

## Detailed Checks

### Copywriting
**Score**: {report['checks']['copywriting']['score']:.2f}
{chr(10).join(f"- {i}" for i in report['checks']['copywriting'].get('issues', []))}

### Images
**Score**: {report['checks']['images']['score']:.2f}
{chr(10).join(f"- {i}" for i in report['checks']['images'].get('issues', []))}

### Video
**Score**: {report['checks']['video']['score']:.2f}
{chr(10).join(f"- {i}" for i in report['checks']['video'].get('issues', []))}

### Consistency
**Score**: {report['checks']['consistency']['score']:.2f}
{chr(10).join(f"- {i}" for i in report['checks']['consistency'].get('issues', []))}

## Issues
{chr(10).join(f"- {i}" for i in report['issues'])}

## Suggestions
{chr(10).join(f"- {s}" for s in report['suggestions'])}

---

## Raw Data
```json
{json.dumps(report, indent=2, ensure_ascii=False)}
```
"""

        self.tools.filesystem.write_file(report_path, markdown)
