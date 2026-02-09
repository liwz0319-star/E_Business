"""
Prompt templates for Image Generation Agent.

Provides prompts for prompt optimization workflow.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImagePrompts:
    """Prompts for image generation workflow."""
    
    # Thought messages
    optimize_start: str = "🎨 正在分析并优化您的图像描述..."
    optimize_complete: str = "✅ 提示词优化完成"
    generate_start: str = "🖼️ 正在生成图像..."
    generate_complete: str = "✅ 图像生成完成"
    persist_start: str = "💾 正在保存图像资产..."
    persist_complete: str = "✅ 图像已保存"
    
    @staticmethod
    def get_optimize_prompt(user_prompt: str, width: int, height: int, style: Optional[str] = None) -> str:
        """
        Generate prompt for DeepSeek to optimize the user's image description.
        
        Args:
            user_prompt: Original user prompt
            width: Target image width
            height: Target image height
            style: Optional artistic style
            
        Returns:
            System prompt for DeepSeek
        """
        base_prompt = f"""You are an expert at crafting prompts for AI image generation.

Your task is to enhance and optimize the following image description to produce the best possible image.

Original description: "{user_prompt}"
Target dimensions: {width}x{height} pixels"""

        if style:
            base_prompt += f"\nTarget Style: {style}"
            
        base_prompt += """

Guidelines:
1. Add specific details about lighting, composition, and style"""
        
        if style:
             base_prompt += f" (emphasizing {style} style)"
             
        base_prompt += """
2. Include artistic direction (photorealistic, illustration, 3D render, etc.)"""

        if not style:
             base_prompt += " matching the description"

        base_prompt += """
3. Describe textures, colors, and atmosphere
4. Keep the core subject matter from the original prompt
5. Make it concise but descriptive (max 200 words)

Output ONLY the optimized prompt, no explanations or prefixes."""
        
        return base_prompt


IMAGE_PROMPTS = ImagePrompts()
