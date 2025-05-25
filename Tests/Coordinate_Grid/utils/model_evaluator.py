import json
import math
from collections import defaultdict

class CoordinateGridEvaluator:
    def __init__(self, dataset_path=None):
        """
        Initialize the evaluator with a dataset.
        
        Args:
            dataset_path: Path to the dataset JSON file.
        """
        if dataset_path is None:
            # Default to dataset.json in the parent directory
            import os
            test_dir = os.path.dirname(os.path.dirname(__file__))
            dataset_path = os.path.join(test_dir, "dataset.json")
        self.dataset_path = dataset_path
        self.load_dataset()
        
    def load_dataset(self):
        """Load the dataset from JSON file."""
        with open(self.dataset_path, 'r') as f:
            self.dataset = json.load(f)
    
    def calculate_distance(self, pred_coord, true_coord):
        """Calculate Euclidean distance between predicted and true coordinates."""
        if not pred_coord or len(pred_coord) != 2:
            return float('inf')
        return math.sqrt((pred_coord[0] - true_coord[0])**2 + (pred_coord[1] - true_coord[1])**2)
    
    def is_coordinate_accurate(self, pred_coord, true_coord, tolerance=10):
        """
        Check if predicted coordinate is within tolerance of true coordinate.
        
        Args:
            pred_coord: Predicted [x, y] coordinate
            true_coord: True [x, y] coordinate  
            tolerance: Maximum distance allowed for a "correct" prediction
            
        Returns:
            bool: True if prediction is within tolerance
        """
        distance = self.calculate_distance(pred_coord, true_coord)
        return distance <= tolerance
    
    def evaluate_square_prediction(self, prediction, ground_truth_square, square_id, tolerance=10):
        """
        Evaluate a single square coordinate prediction.
        
        Args:
            prediction: Model's predicted coordinate [x, y] or None
            ground_truth_square: Ground truth square data with 'center' coordinate
            square_id: ID of the square (0-4)
            tolerance: Maximum distance for correct prediction
            
        Returns:
            dict: Evaluation metrics for this square
        """
        true_coord = [ground_truth_square['x'], ground_truth_square['y']]
        
        if prediction is None or len(prediction) != 2:
            return {
                "square_id": square_id,
                "predicted": None,
                "ground_truth": true_coord,
                "distance": float('inf'),
                "is_correct": False,
                "tolerance_used": tolerance
            }
        
        distance = self.calculate_distance(prediction, true_coord)
        is_correct = distance <= tolerance
        
        return {
            "square_id": square_id,
            "predicted": prediction,
            "ground_truth": true_coord,
            "distance": distance,
            "is_correct": is_correct,
            "tolerance_used": tolerance
        }
    
    def evaluate_image(self, image_idx, model_predictions, tolerance=10):
        """
        Evaluate model predictions for a single image.
        
        Args:
            image_idx: Index of the image in the dataset
            model_predictions: List of predicted coordinates for squares 0-4
            tolerance: Maximum distance for correct prediction
            
        Returns:
            dict: Evaluation results for this image
        """
        if image_idx >= len(self.dataset):
            raise IndexError(f"Image index {image_idx} out of range")
        dataset_entry = self.dataset[image_idx]
        ground_truth_squares = dataset_entry['ground_truth']
        
        # Ensure we have predictions for all 5 squares
        while len(model_predictions) < 5:
            model_predictions.append(None)
        
        square_results = []
        for square_id in range(5):
            prediction = model_predictions[square_id] if square_id < len(model_predictions) else None
            ground_truth_square = next((sq for sq in ground_truth_squares if sq['square_id'] == square_id), None)
            if ground_truth_square is None:
                continue
            
            result = self.evaluate_square_prediction(prediction, ground_truth_square, square_id, tolerance)
            square_results.append(result)
        
        # Calculate image-level metrics
        correct_squares = sum(1 for r in square_results if r['is_correct'])
        total_squares = len(square_results)
        
        return {
            "image_path": dataset_entry['image_path'],
            "image_idx": image_idx,
            "square_results": square_results,
            "squares_correct": correct_squares,
            "total_squares": total_squares,
            "image_accuracy": correct_squares / total_squares if total_squares > 0 else 0,
            "tolerance_used": tolerance
        }
    
    def parse_model_predictions(self, raw_predictions):
        """
        Parse model predictions from the new JSON format to coordinate pairs.
        
        Args:
            raw_predictions: List of prediction objects with format:
                [{"id": 0, "x": 45, "y": 123}, {"id": 1, "x": 156, "y": 267}, ...]
                
        Returns:
            List of [x, y] coordinate pairs ordered by ID
        """
        if not raw_predictions:
            return [None] * 5
        
        # Create array to hold predictions in ID order
        predictions = [None] * 5
        
        for pred in raw_predictions:
            if isinstance(pred, dict) and 'id' in pred and 'x' in pred and 'y' in pred:
                pred_id = pred['id']
                if 0 <= pred_id <= 4:
                    predictions[pred_id] = [pred['x'], pred['y']]
        
        return predictions
    
    def evaluate_model(self, model_responses, tolerance=10):
        """
        Evaluate a model's responses across all test images.
        
        Args:
            model_responses: List of response objects with format:
                {
                    "image_path": "path/to/image.png",
                    "predictions": [{"id": 0, "x": 45, "y": 123}, {"id": 1, "x": 156, "y": 267}, ...]
                }
            tolerance: Maximum distance for correct prediction
            
        Returns:
            dict: Complete evaluation results
        """
        # Create lookup from image path to dataset index
        image_path_to_idx = {}
        for idx, entry in enumerate(self.dataset):
            # Normalize path for consistent matching
            normalized_path = entry['image_path'].replace("\\", "/")
            image_path_to_idx[normalized_path] = idx
        
        image_results = []
        for response_item in model_responses:
            # Normalize response path
            resp_path = response_item["image_path"].replace("\\", "/")
            if resp_path not in image_path_to_idx and not resp_path.startswith("assets/"):
                resp_path = "assets/" + resp_path
            
            if resp_path not in image_path_to_idx:
                print(f"Warning: No matching dataset entry found for {resp_path}")
                continue
                
            idx = image_path_to_idx[resp_path]            # Parse responses - format [{"id":0,"x":x,"y":y},...]
            raw_predictions = response_item["responses"]
            parsed_predictions = self.parse_model_predictions(raw_predictions)
            
            image_result = self.evaluate_image(idx, parsed_predictions, tolerance)
            image_results.append(image_result)
          # Calculate overall metrics
        total_squares = sum(r["total_squares"] for r in image_results)
        total_squares_correct = sum(r["squares_correct"] for r in image_results)
        
        # Calculate average distance
        all_distances = []
        for result in image_results:
            for square_result in result["square_results"]:
                if square_result["distance"] != float('inf'):
                    all_distances.append(square_result["distance"])
        
        average_distance = sum(all_distances) / len(all_distances) if all_distances else float('inf')
        
        # Group results by square position for analysis
        by_square_position = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for result in image_results:
            for square_result in result["square_results"]:
                square_id = square_result["square_id"]
                by_square_position[square_id]["total"] += 1
                if square_result["is_correct"]:
                    by_square_position[square_id]["correct"] += 1
        
        # Calculate accuracy by square position
        square_position_accuracies = {
            position: metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0
            for position, metrics in by_square_position.items()
        }
        return {
            "overall_accuracy": total_squares_correct / total_squares if total_squares > 0 else 0,
            "average_distance": average_distance,
            "total_images": len(image_results),
            "total_squares": total_squares,
            "total_squares_correct": total_squares_correct,
            "accuracy_by_square_position": square_position_accuracies,
            "tolerance_used": tolerance,
            "image_results": image_results
        }
    
    def save_evaluation(self, evaluation, output_path="evaluation_results.json"):
        """Save evaluation results to a JSON file."""
        with open(output_path, 'w') as f:
            json.dump(evaluation, f, indent=2)


if __name__ == "__main__":
    # Example showing evaluator usage
    evaluator = CoordinateGridEvaluator()
    print("CoordinateGridEvaluator initialized and ready to use.")
    print("Use evaluate_model() with a list of response objects in the format:")
    print('{')
    print('    "image_path": "path/to/image.png",')
    print('    "predictions": [{"id": 0, "x": 45, "y": 123}, {"id": 1, "x": 156, "y": 267}, ...]')
    print('}')
    print()
    print("Coordinates should be in JSON format with bottom-left origin (0,0) to (512,512)")
    print("Default tolerance for 'correct' predictions is 10 pixels")
