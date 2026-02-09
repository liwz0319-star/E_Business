"""
Image Generation Request Entity.

Domain entity for image generation requests.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ImageGenerationRequest:
    """Domain entity for an image generation request.
    
    Contains the parameters needed to generate an image.
    
    Attributes:
        prompt: Text description of the image to generate
        width: Desired image width in pixels
        height: Desired image height in pixels
        style: Optional style modifier (e.g., "photorealistic", "cartoon")
        negative_prompt: Optional text describing what to avoid
        num_inference_steps: Number of inference steps for generation
        guidance_scale: Guidance scale for prompt adherence
    """
    prompt: str
    width: int = 512
    height: int = 512
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    
    def to_dict(self) -> dict:
        """Convert request to dictionary."""
        return {
            "prompt": self.prompt,
            "width": self.width,
            "height": self.height,
            "style": self.style,
            "negative_prompt": self.negative_prompt,
            "num_inference_steps": self.num_inference_steps,
            "guidance_scale": self.guidance_scale,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ImageGenerationRequest":
        """Create request from dictionary."""
        return cls(
            prompt=data.get("prompt", ""),
            width=data.get("width", 512),
            height=data.get("height", 512),
            style=data.get("style"),
            negative_prompt=data.get("negative_prompt"),
            num_inference_steps=data.get("num_inference_steps", 50),
            guidance_scale=data.get("guidance_scale", 7.5),
        )
