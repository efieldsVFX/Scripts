"""Generate a simple logo for the dashboard"""

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from pathlib import Path

def create_logo():
    # Create a new image with a white background
    img = PIL.Image.new('RGB', (200, 200), 'white')
    draw = PIL.ImageDraw.Draw(img)
    
    # Draw a circle
    draw.ellipse([40, 40, 160, 160], outline='#007bff', width=4)
    
    # Draw the letters "SM"
    try:
        font = PIL.ImageFont.truetype("arial.ttf", 60)
    except:
        font = PIL.ImageFont.load_default()
    
    draw.text((60, 70), "SM", fill='#007bff', font=font)
    
    # Save the logo
    save_path = Path(__file__).parent / 'logo.png'
    img.save(save_path)
    
if __name__ == "__main__":
    create_logo()
