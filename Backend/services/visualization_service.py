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
        """Generate visualization for Eye_Test test with character-level highlighting."""
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
        asset_metadata = None
        for item in dataset:
            if asset_id in item['image_path']:
                ground_truth = item['ground_truth']
                asset_metadata = item['metadata']
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
        
        # Generate enhanced visualization
        image = Image.open(image_path).convert('RGBA')
        
        # Create a separate overlay for highlights
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Font mapping for Eye Test
        font_paths = {
            "Arial": "arial.ttf",
            "Times New Roman": "times.ttf",
            "Comic Sans": "comic.ttf",
            "Courier": "cour.ttf",
            "Verdana": "verdana.ttf"
        }        # Get the font used in this asset
        asset_font_name = asset_metadata.get('font', 'Arial')
        
        # Constants from Eye Test configuration
        VERTICAL_SPACING = 3
        IMAGE_WIDTH = 512
        
        # Calculate row positions using the EXACT same logic as asset generator
        y_position = 50  # Starting position from asset generator
        
        for i, (gt_row, pred_row) in enumerate(zip(ground_truth, predictions)):
            if 'text' not in pred_row:
                # Still need to advance y_position even if no prediction
                font_size = gt_row['size']
                y_position += int(font_size * VERTICAL_SPACING)
                continue
                
            gt_text = gt_row['text']
            pred_text = pred_row['text']
            font_size = gt_row['size']
            
            # Load the matching font and size
            try:
                if asset_font_name in font_paths:
                    font = ImageFont.truetype(font_paths[asset_font_name], size=int(font_size))
                else:
                    font = ImageFont.truetype("arial.ttf", size=int(font_size))
            except:
                font = ImageFont.load_default()
            
            # Calculate text positioning (centered, EXACTLY same as original)
            bbox = draw.textbbox((0, 0), gt_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_position = (IMAGE_WIDTH - text_width) // 2            # Position for markers (below the original text)
            marker_y_position = y_position + text_height + 4  # 4 pixels below the original text
            
            # Character-by-character comparison with colored dashes
            max_len = max(len(gt_text), len(pred_text))
            current_x = x_position
            
            for char_idx in range(max_len):
                gt_char = gt_text[char_idx] if char_idx < len(gt_text) else ''
                pred_char = pred_text[char_idx] if char_idx < len(pred_text) else ''
                
                # Only place markers if both characters exist
                if gt_char and pred_char:
                    # Calculate character width for centering the marker
                    char_bbox = draw.textbbox((0, 0), gt_char, font=font)
                    char_width = char_bbox[2] - char_bbox[0]
                    marker_x = current_x + char_width // 2  # Center of character
                    
                    if gt_char == pred_char:
                        # Green dash for correct characters
                        draw.text((marker_x - 3, marker_y_position), "—", 
                                 fill=(0, 200, 0, 255), font=font)  # Green dash
                    else:
                        # Red dash for incorrect characters
                        draw.text((marker_x - 3, marker_y_position), "—", 
                                 fill=(255, 0, 0, 255), font=font)  # Red dash
                
                # Move to next character position (use ground truth character for spacing)
                if char_idx < len(gt_text):
                    spacing_char = gt_text[char_idx]
                    char_bbox = draw.textbbox((0, 0), spacing_char, font=font)
                    current_x += char_bbox[2] - char_bbox[0]
            
            # Update y_position for next row using EXACT same logic as asset generator
            y_position += int(font_size * VERTICAL_SPACING)
        
        # Composite the overlay onto the original image
        final_image = Image.alpha_composite(image, overlay)
        
        # Convert to RGB for JPEG compatibility
        final_image = final_image.convert('RGB')
        
        # Convert to base64
        buffer = BytesIO()
        final_image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "test_type": "Eye_Test",
            "model": model,
            "asset_id": asset_id,
            "visualization_image": image_b64,
            "metadata": {
                "ground_truth": ground_truth,
                "predictions": predictions,
                "image_dimensions": {"width": final_image.width, "height": final_image.height}
            }
        }

# Global service instance
visualization_service = VisualizationService()
