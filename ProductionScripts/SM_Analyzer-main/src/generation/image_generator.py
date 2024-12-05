"""
Image Generator
Handles image generation using Stable Diffusion and other models.
"""

import torch
from typing import Optional, List, Union, Dict
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import requests
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from utils import logger, MODEL_CONFIG, PROJECT_ROOT

class ImageGenerator:
    def __init__(self, 
                 model_id: str = "runwayml/stable-diffusion-v1-5",
                 device: str = "cuda" if torch.cuda.is_available() else "cpu",
                 output_dir: Optional[Path] = None):
        """
        Initialize image generator
        
        Args:
            model_id (str): Hugging Face model ID
            device (str): Device to use for generation ('cuda' or 'cpu')
            output_dir (Path, optional): Directory to save generated images
        """
        self.model_id = model_id
        self.device = device
        self.output_dir = output_dir or PROJECT_ROOT / "output" / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize the pipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            
            # Use DPM-Solver++ scheduler for faster inference
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            # Move to device
            self.pipe = self.pipe.to(device)
            
            # Enable memory efficient attention if using cuda
            if device == "cuda":
                self.pipe.enable_attention_slicing()
            
            logger.info(f"Image generator initialized using {model_id} on {device}")
            
        except Exception as e:
            logger.error(f"Error initializing image generator: {str(e)}")
            raise

    def generate_image(self,
                      prompt: str,
                      negative_prompt: str = "",
                      num_images: int = 1,
                      size: tuple = (512, 512),
                      guidance_scale: float = 7.5,
                      num_inference_steps: int = 50,
                      seed: Optional[int] = None) -> List[Image.Image]:
        """
        Generate images from text prompt
        
        Args:
            prompt (str): Text prompt for image generation
            negative_prompt (str): Text to guide what not to generate
            num_images (int): Number of images to generate
            size (tuple): Image size (width, height)
            guidance_scale (float): Guidance scale for generation
            num_inference_steps (int): Number of denoising steps
            seed (int, optional): Random seed for reproducibility
            
        Returns:
            List[Image.Image]: Generated images
        """
        try:
            # Set random seed if provided
            if seed is not None:
                torch.manual_seed(seed)
                
            logger.info(f"Generating {num_images} image(s) for prompt: {prompt}")
            
            # Generate images
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_images_per_prompt=num_images,
                height=size[1],
                width=size[0],
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps
            )
            
            # Check for safety issues
            if hasattr(result, "nsfw_content_detected"):
                nsfw_detected = any(result.nsfw_content_detected)
                if nsfw_detected:
                    logger.warning("NSFW content detected in generated images")
            
            return result.images
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise

    def save_images(self,
                   images: List[Image.Image],
                   base_filename: str,
                   format: str = "PNG") -> List[Path]:
        """
        Save generated images to disk
        
        Args:
            images (List[Image.Image]): List of PIL Images
            base_filename (str): Base filename for saving
            format (str): Image format to save as
            
        Returns:
            List[Path]: Paths to saved images
        """
        saved_paths = []
        for i, image in enumerate(images):
            try:
                # Create filename with index if multiple images
                filename = f"{base_filename}_{i}.{format.lower()}" if len(images) > 1 else f"{base_filename}.{format.lower()}"
                filepath = self.output_dir / filename
                
                # Save image
                image.save(filepath, format=format)
                saved_paths.append(filepath)
                logger.info(f"Saved image to {filepath}")
                
            except Exception as e:
                logger.error(f"Error saving image {i}: {str(e)}")
                continue
                
        return saved_paths

    def generate_variations(self,
                          image: Union[Image.Image, Path, str],
                          num_variations: int = 1,
                          strength: float = 0.8,
                          guidance_scale: float = 7.5,
                          seed: Optional[int] = None) -> List[Image.Image]:
        """
        Generate variations of an existing image
        
        Args:
            image (Union[Image.Image, Path, str]): Input image or path
            num_variations (int): Number of variations to generate
            strength (float): Strength of variation (0-1)
            guidance_scale (float): Guidance scale for generation
            seed (int, optional): Random seed for reproducibility
            
        Returns:
            List[Image.Image]: Generated image variations
        """
        try:
            # Load image if path provided
            if isinstance(image, (str, Path)):
                image = Image.open(image).convert("RGB")
            
            # Set random seed if provided
            if seed is not None:
                torch.manual_seed(seed)
            
            logger.info(f"Generating {num_variations} variation(s) of input image")
            
            # Generate variations
            result = self.pipe(
                image=image,
                strength=strength,
                guidance_scale=guidance_scale,
                num_images_per_prompt=num_variations
            )
            
            return result.images
            
        except Exception as e:
            logger.error(f"Error generating image variations: {str(e)}")
            raise

    def image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 string
        
        Args:
            image (Image.Image): PIL Image
            format (str): Image format
            
        Returns:
            str: Base64 encoded image string
        """
        buffered = BytesIO()
        image.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode()

    def base64_to_image(self, base64_string: str) -> Image.Image:
        """
        Convert base64 string to PIL Image
        
        Args:
            base64_string (str): Base64 encoded image string
            
        Returns:
            Image.Image: PIL Image
        """
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data)) 