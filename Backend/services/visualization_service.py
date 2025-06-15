"""
Visualization service for generating overlaid test images with model predictions.
"""

import os
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class VisualizationService:
    def __init__(self):
        self.tests_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Tests")
    
    def generate_visualization(self, test_type: str, model: str, asset_id: str) -> Dict[str, Any]:
        """
        Generate visualization overlay for a specific test, model, and asset.
        
        Args:
            test_type: The test type (e.g., "Coordinate_Grid", "Eye_Test")
            model: The model name (e.g., "claude-3-5-haiku")
            asset_id: The asset identifier (e.g., "coordinate_grid_1748135594214")
            
        Returns:
            Dict containing base64 encoded visualization and metadata
        """
        try:
            if test_type == "Coordinate_Grid":
                return self._generate_coordinate_grid_visualization(model, asset_id)
            elif test_type == "Eye_Test":
                return self._generate_eye_test_visualization(model, asset_id)
            else:
                raise ValueError(f"Unsupported test type: {test_type}")
                
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            raise
    
    def _generate_coordinate_grid_visualization(self, model: str, asset_id: str) -> Dict[str, Any]:
        """Generate visualization for Coordinate_Grid test."""
        test_dir = os.path.join(self.tests_dir, "Coordinate_Grid")
        
        # Load original image
        image_path = os.path.join(test_dir, "assets", f"{asset_id}.png")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Asset image not found: {image_path}")
        
        # Load dataset for ground truth
        dataset_path = os.path.join(test_dir, "dataset.json")
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        # Find ground truth for this asset
        ground_truth = None
        for item in dataset:
            if asset_id in item['image_path']:
                ground_truth = item['ground_truth']
                break
        
        if ground_truth is None:
            raise ValueError(f"Ground truth not found for asset: {asset_id}")
        
        # Load model responses
        responses_path = os.path.join(test_dir, "responses", f"{model}_responses.json")
        if not os.path.exists(responses_path):
            raise FileNotFoundError(f"Model responses not found: {responses_path}")
        
        with open(responses_path, 'r') as f:
            responses = json.load(f)
        
        # Find predictions for this asset
        predictions = None
        for response in responses:
            if asset_id in response['image_path']:
                predictions = response['responses']
                break
        
        if predictions is None:
            raise ValueError(f"Predictions not found for asset: {asset_id}")
        
        # Generate visualization
        image = Image.open(image_path).convert('RGBA')
        draw = ImageDraw.Draw(image)
        
        # Draw red X marks where model guessed
        for pred in predictions:
            if 'x' in pred and 'y' in pred:
                x, y = pred['x'], pred['y']
                # Convert from bottom-left origin to top-left origin for PIL
                y = image.height - y
                
                # Draw red X (using lines)
                size = 8
                draw.line([(x-size, y-size), (x+size, y+size)], fill='red', width=3)
                draw.line([(x-size, y+size), (x+size, y-size)], fill='red', width=3)
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "test_type": "Coordinate_Grid",
            "model": model,
            "asset_id": asset_id,
            "visualization_image": image_b64,
            "metadata": {
                "ground_truth": ground_truth,
                "predictions": predictions,
                "image_dimensions": {"width": image.width, "height": image.height}
            }
        }
    
    def _generate_eye_test_visualization(self, model: str, asset_id: str) -> Dict[str, Any]:
        """Generate visualization for Eye_Test test."""
        test_dir = os.path.join(self.tests_dir, "Eye_Test")
        
        # Load original image
        image_path = os.path.join(test_dir, "assets", f"{asset_id}.png")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Asset image not found: {image_path}")
        
        # Load dataset for ground truth
        dataset_path = os.path.join(test_dir, "dataset.json")
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        # Find ground truth for this asset
        ground_truth = None
        for item in dataset:
            if asset_id in item['image_path']:
                ground_truth = item['ground_truth']
                break
        
        if ground_truth is None:
            raise ValueError(f"Ground truth not found for asset: {asset_id}")
        
        # Load model responses
        responses_path = os.path.join(test_dir, "responses", f"{model}_responses.json")
        if not os.path.exists(responses_path):
            raise FileNotFoundError(f"Model responses not found: {responses_path}")
        
        with open(responses_path, 'r') as f:
            responses = json.load(f)
        
        # Find predictions for this asset
        predictions = None
        for response in responses:
            if asset_id in response['image_path']:
                predictions = response['responses']
                break
        
        if predictions is None:
            raise ValueError(f"Predictions not found for asset: {asset_id}")
        
        # Generate visualization
        image = Image.open(image_path).convert('RGBA')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Add red text underneath each row showing what the model predicted
        # This is a simplified approach - you may need to adjust positioning based on your eye test layout
        row_height = image.height // len(ground_truth) if ground_truth else 50
        
        for i, (gt_row, pred_row) in enumerate(zip(ground_truth, predictions)):
            if 'text' in pred_row:
                y_position = (i + 1) * row_height - 25  # Position below each row
                pred_text = f"Model: {pred_row['text']}"
                
                # Draw red text
                draw.text((10, y_position), pred_text, fill='red', font=font)
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "test_type": "Eye_Test",
            "model": model,
            "asset_id": asset_id,
            "visualization_image": image_b64,
            "metadata": {
                "ground_truth": ground_truth,
                "predictions": predictions,
                "image_dimensions": {"width": image.width, "height": image.height}
            }
        }

# Global service instance
visualization_service = VisualizationService()
