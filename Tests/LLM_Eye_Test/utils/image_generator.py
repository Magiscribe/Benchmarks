import os
import random
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from test_config import STANDARD_FONT_SIZES, CHARS_PER_ROW, VERTICAL_SPACING, IMAGE_WIDTH, IMAGE_HEIGHT, FONTS, ALPHABET

class EyeChartGenerator:
    def __init__(self, output_dir="assets"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.fonts = FONTS
        self.alphabet = ALPHABET
        
    def generate_random_text(self, length):
        return ''.join(random.choice(self.alphabet) for _ in range(length))
    
    def create_eye_chart(self, font_name, chars_per_row=CHARS_PER_ROW, 
                         font_sizes=STANDARD_FONT_SIZES, 
                         width=IMAGE_WIDTH, height=IMAGE_HEIGHT):
        """
        Create an eye chart image with standardized font sizes.
        
        Args:
            font_name: Name of the font to use
            chars_per_row: Number of characters per row
            font_sizes: List of font sizes to use (default: STANDARD_FONT_SIZES)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Tuple of (filepath, metadata)
        """
        if font_name not in self.fonts:
            raise ValueError(f"Font {font_name} not supported. Available fonts: {list(self.fonts.keys())}")
            
        # Create a new white image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Font path - in production would need actual system font paths
        try:
            font_path = self.fonts[font_name]
        except KeyError:
            font_path = self.fonts["Arial"]  # Default to Arial if font not found
        
        # Track the text and size for each row
        row_data = []
        
        # Draw rows of text
        y_position = 50  # Start position from top
        
        for row, font_size in enumerate(font_sizes):
            # Generate random text for this row
            text = self.generate_random_text(chars_per_row)
            
            try:
                font = ImageFont.truetype(font_path, size=int(font_size))
            except IOError:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Draw text centered on the image
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (width - text_width) // 2
            
            draw.text((x_position, y_position), text, fill="black", font=font)
            
            # Store row data - using 0-indexing
            row_data.append({
                "row": row,  # 0-indexed rows
                "text": text,
                "size": font_size
            })
            
            # Update for next row with more spacing for better readability
            y_position += int(font_size * VERTICAL_SPACING)
        
        # Create filename with font prefix: Font_timestamp.png
        timestamp = int(time.time() * 1000)
        filename = f"{font_name.replace(' ', '_')}_{timestamp}.png"
        # Save directly to assets/ directory (no subdirectories)
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        # Return metadata
        metadata = {
            "font": font_name,
            "font_sizes": font_sizes,
            "num_rows": len(font_sizes),
            "chars_per_row": chars_per_row,
            "row_data": row_data
        }
        
        return filepath, metadata
    
    def generate_test_set(self, fonts=None, num_images_per_font=1):
        """
        Generate a set of test images with standardized font sizes.
        
        Args:
            fonts: List of fonts to use. If None, uses all available fonts.
            num_images_per_font: Number of images to generate per font.
            
        Returns:
            List of dicts with image paths and metadata.
        """
        if fonts is None:
            fonts = list(self.fonts.keys())
        
        results = []
        
        for font in fonts:
            for i in range(num_images_per_font):
                # Add a small delay to ensure unique timestamps
                if i > 0:
                    time.sleep(1)
                
                # Use standard font sizes but vary character content
                filepath, metadata = self.create_eye_chart(
                    font_name=font,
                    chars_per_row=CHARS_PER_ROW,
                    font_sizes=STANDARD_FONT_SIZES
                )
                
                results.append({
                    "image_path": filepath,
                    "metadata": metadata
                })
                
                print(f"Generated image {i+1}/{num_images_per_font} for {font}: {filepath}")
        
        return results

if __name__ == "__main__":
    generator = EyeChartGenerator()
    # Test with a single image
    filepath, metadata = generator.create_eye_chart("Arial")
    print(f"Created eye chart at {filepath}")
    print(f"Metadata: {metadata}")
    
    # Or generate a whole test set
    # test_set = generator.generate_test_set()
    # print(f"Generated {len(test_set)} test images")