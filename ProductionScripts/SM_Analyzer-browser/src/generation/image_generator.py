"""
Image Generator Module
Generates images from text descriptions using AI models
"""

import logging
import os
from typing import Dict, List, Optional
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from PIL import Image
import numpy as np

from src.utils.logger import get_logger
from src.config.model_config import MODEL_CONFIG

logger = get_logger(__name__)

class ImageGenerator:
    def __init__(self, model_path: Optional[str] = None):
        """Initialize image generator"""
        self.model_path = model_path or MODEL_CONFIG['stable_diffusion']['model_path']
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        
    def load_model(self):
        """Load the image generation model"""
        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.pipe = self.pipe.to(self.device)
            logger.info(f"Loaded image generation model on {self.device}")
        except Exception as e:
            logger.error(f"Error loading image generation model: {str(e)}")
            raise
            
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512
    ) -> Optional[Image.Image]:
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of the desired image
            negative_prompt: Text describing what to avoid in the image
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            width: Output image width
            height: Output image height
            
        Returns:
            Generated PIL Image or None if generation fails
        """
        try:
            if self.pipe is None:
                self.load_model()
                
            with autocast(self.device):
                image = self.pipe(
                    prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height
                ).images[0]
                
            return image
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
            
    def generate_variations(
        self,
        prompt: str,
        num_variations: int = 4,
        **kwargs
    ) -> List[Image.Image]:
        """
        Generate multiple variations of an image from the same prompt
        
        Args:
            prompt: Text description of the desired image
            num_variations: Number of variations to generate
            **kwargs: Additional arguments passed to generate_image
            
        Returns:
            List of generated PIL Images
        """
        images = []
        for _ in range(num_variations):
            image = self.generate_image(prompt, **kwargs)
            if image is not None:
                images.append(image)
                
        return images