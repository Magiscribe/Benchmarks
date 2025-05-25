import os
import json
import time
from typing import List, Dict, Any
from .asset_generator import CoordinateGridGenerator

class DatasetCreator:
    """Creates datasets for the LLM Coordinate Grid benchmark."""
    
    def __init__(self, output_file: str = "dataset.json"):
        """
        Initialize the dataset creator.
        
        Args:
            output_file: Path to save the dataset JSON file
        """
        self.output_file = output_file
    
    def create_dataset(self, 
                      num_images: int = 10,
                      image_width: int = 512,
                      image_height: int = 512,
                      square_size: int = 5,
                      num_squares: int = 5,
                      min_distance: int = 20,
                      output_dir: str = "assets") -> List[Dict[str, Any]]:
        """
        Create a complete dataset of coordinate grid test images.
        
        Args:
            num_images: Number of test images to generate
            image_width: Width of each image
            image_height: Height of each image
            square_size: Size of each square
            num_squares: Number of squares per image
            min_distance: Minimum distance between square centers
            output_dir: Directory to save images
            
        Returns:
            List of dataset entries with image paths and metadata
        """
        generator = CoordinateGridGenerator(output_dir=output_dir)
        dataset = []
        
        print(f"Generating {num_images} coordinate grid test images...")
        
        for i in range(num_images):
            # Generate test image
            image_path, squares_metadata = generator.generate_test_image(
                image_width=image_width,
                image_height=image_height,
                square_size=square_size,
                num_squares=num_squares,
                min_distance=min_distance
            )
            
            # Create ground truth - coordinates of squares from left to right
            ground_truth = []
            for square in squares_metadata:
                ground_truth.append({
                    "square_id": square["square_id"],
                    "x": square["center_x"],
                    "y": square["center_y"]
                })
            
            # Create dataset entry
            dataset_entry = {
                "image_path": image_path,
                "metadata": {
                    "image_width": image_width,
                    "image_height": image_height,
                    "square_size": square_size,
                    "num_squares": num_squares,
                    "min_distance": min_distance,
                    "coordinate_system": "bottom_left_origin"
                },
                "ground_truth": ground_truth
            }
            
            dataset.append(dataset_entry)
            
            if (i + 1) % 5 == 0 or (i + 1) == num_images:
                print(f"Generated {i + 1}/{num_images} images...")
        
        # Save dataset to JSON file
        with open(self.output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Dataset saved to {self.output_file}")
        return dataset
    
    def load_dataset(self) -> List[Dict[str, Any]]:
        """
        Load an existing dataset from file.
        
        Returns:
            List of dataset entries
        """
        if not os.path.exists(self.output_file):
            raise FileNotFoundError(f"Dataset file {self.output_file} not found")
        
        with open(self.output_file, 'r') as f:
            return json.load(f)
    
    def get_dataset_stats(self, dataset: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get statistics about the dataset.
        
        Args:
            dataset: Dataset to analyze. If None, loads from file.
            
        Returns:
            Dictionary with dataset statistics
        """
        if dataset is None:
            dataset = self.load_dataset()
        
        total_images = len(dataset)
        total_squares = sum(len(entry["ground_truth"]) for entry in dataset)
        
        # Analyze coordinate distribution
        all_x_coords = []
        all_y_coords = []
        
        for entry in dataset:
            for square in entry["ground_truth"]:
                all_x_coords.append(square["x"])
                all_y_coords.append(square["y"])
        
        stats = {
            "total_images": total_images,
            "total_squares": total_squares,
            "squares_per_image": total_squares // total_images if total_images > 0 else 0,
            "coordinate_ranges": {
                "x_min": min(all_x_coords) if all_x_coords else 0,
                "x_max": max(all_x_coords) if all_x_coords else 0,
                "y_min": min(all_y_coords) if all_y_coords else 0,
                "y_max": max(all_y_coords) if all_y_coords else 0
            }
        }
        
        return stats
