import os
import random
import time
from PIL import Image, ImageDraw
from typing import List, Tuple, Dict, Any
import json

class CoordinateGridGenerator:
    """Generates test images with black squares on white background for coordinate testing."""
    
    def __init__(self, output_dir: str = "assets"):
        """
        Initialize the coordinate grid generator.
        
        Args:
            output_dir: Directory to save generated images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_square_positions(self, 
                                image_width: int, 
                                image_height: int, 
                                square_size: int, 
                                num_squares: int, 
                                min_distance: int) -> List[Tuple[int, int]]:
        """
        Generate random positions for squares ensuring they don't overlap.
        
        Args:
            image_width: Width of the image
            image_height: Height of the image 
            square_size: Size of each square (assumed square)
            num_squares: Number of squares to place
            min_distance: Minimum distance between square centers
            
        Returns:
            List of (x, y) coordinates for square centers
        """
        positions = []
        max_attempts = 1000
          # Ensure squares stay within image bounds with border distance
        half_square = square_size // 2
        border_distance = min_distance // 2  # Half of minimum distance between squares
        min_x = max(half_square, border_distance)
        max_x = min(image_width - half_square, image_width - border_distance)
        min_y = max(half_square, border_distance)
        max_y = min(image_height - half_square, image_height - border_distance)
        
        for _ in range(num_squares):
            attempts = 0
            while attempts < max_attempts:
                # Generate random position
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                  # Check if this position is far enough from existing squares
                # Ensure at least min_distance pixels separation in both X and Y directions
                valid_position = True
                for existing_x, existing_y in positions:
                    x_distance = abs(x - existing_x)
                    y_distance = abs(y - existing_y)
                    if x_distance < min_distance or y_distance < min_distance:
                        valid_position = False
                        break
                
                if valid_position:
                    positions.append((x, y))
                    break
                    
                attempts += 1
            
            if attempts == max_attempts:
                # If we can't find a valid position, just place it anyway
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                positions.append((x, y))
        
        return positions
    
    def create_coordinate_grid_image(self, 
                                   image_width: int = 512,
                                   image_height: int = 512,
                                   square_size: int = 5,
                                   num_squares: int = 5,
                                   min_distance: int = 20,
                                   background_color: Tuple[int, int, int] = (255, 255, 255),
                                   square_color: Tuple[int, int, int] = (0, 0, 0)) -> Tuple[Image.Image, List[Dict[str, Any]]]:
        """
        Create a coordinate grid test image with randomly placed squares.
        
        Args:
            image_width: Width of the image
            image_height: Height of the image
            square_size: Size of each square
            num_squares: Number of squares to place
            min_distance: Minimum distance between square centers
            background_color: RGB color for background
            square_color: RGB color for squares
            
        Returns:
            Tuple of (PIL Image, list of square metadata with coordinates)
        """
        # Create image with white background
        image = Image.new('RGB', (image_width, image_height), background_color)
        draw = ImageDraw.Draw(image)
        
        # Generate square positions
        positions = self.generate_square_positions(
            image_width, image_height, square_size, num_squares, min_distance
        )
          # Draw squares and collect metadata
        squares_metadata = []
        for i, (center_x, center_y) in enumerate(positions):
            # Calculate square bounds (center-based)
            half_size = square_size // 2
            left = center_x - half_size
            top = center_y - half_size
            right = center_x + half_size
            bottom = center_y + half_size
            
            # Draw the square
            draw.rectangle([left, top, right, bottom], fill=square_color)
            
            # Convert to our coordinate system (bottom-left origin)
            # PIL uses top-left origin, we want bottom-left
            coord_x = center_x
            coord_y = image_height - center_y
            
            squares_metadata.append({
                "center_x": coord_x,
                "center_y": coord_y,
                "pil_center_x": center_x,  # Store original PIL coordinates for debugging
                "pil_center_y": center_y
            })
        
        # Sort squares by x-coordinate (left to right) and assign proper IDs
        squares_metadata.sort(key=lambda s: s["center_x"])
        
        # Assign square_id based on left-to-right order (0, 1, 2, 3, 4)
        for i, square in enumerate(squares_metadata):
            square["square_id"] = i
        
        return image, squares_metadata
    
    def generate_test_image(self, 
                          image_width: int = 512,
                          image_height: int = 512,
                          square_size: int = 5,
                          num_squares: int = 5,
                          min_distance: int = 20) -> str:
        """
        Generate a single test image and save it.
        
        Args:
            image_width: Width of the image
            image_height: Height of the image
            square_size: Size of each square
            num_squares: Number of squares to place
            min_distance: Minimum distance between square centers
            
        Returns:
            Path to the saved image file
        """
        # Generate unique filename with timestamp
        timestamp = str(int(time.time() * 1000))
        filename = f"coordinate_grid_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create the image
        image, metadata = self.create_coordinate_grid_image(
            image_width, image_height, square_size, num_squares, min_distance
        )
        
        # Save the image
        image.save(filepath)
        
        return filepath, metadata
