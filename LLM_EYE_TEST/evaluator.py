import json
from collections import defaultdict
import statistics

class VisionModelEvaluator:
    def __init__(self, dataset_path="dataset.json"):
        """
        Initialize the evaluator with a dataset.
        
        Args:
            dataset_path: Path to the dataset JSON file.
        """
        self.dataset_path = dataset_path
        self.load_dataset()
        
    def load_dataset(self):
        """Load the dataset from JSON file."""
        with open(self.dataset_path, 'r') as f:
            self.dataset = json.load(f)
            
    def evaluate_row(self, ground_truth, prediction):
        """
        Evaluate a single row prediction.
        
        Args:
            ground_truth: The ground truth text string.
            prediction: The model's prediction text string.
            
        Returns:
            dict: Evaluation metrics for this row.
        """
        # Calculate character-level accuracy
        min_len = min(len(ground_truth), len(prediction))
        max_len = max(len(ground_truth), len(prediction))
        
        correct_chars = sum(1 for i in range(min_len) if ground_truth[i] == prediction[i])
        char_accuracy = correct_chars / max_len if max_len > 0 else 1.0
        
        # Calculate exact match
        exact_match = ground_truth == prediction
        
        return {
            "ground_truth": ground_truth,
            "prediction": prediction,
            "char_accuracy": char_accuracy,
            "exact_match": exact_match,
            "correct_chars": correct_chars,
            "total_chars": max_len
        }
        
    def evaluate_image(self, image_idx, model_response):
        """
        Evaluate model response for a single image.
        
        Args:
            image_idx: Index of the image in the dataset.
            model_response: List of dicts with format [{row: int, text: str}].
            
        Returns:
            dict: Evaluation metrics for this image.
        """
        if image_idx >= len(self.dataset):
            raise ValueError(f"Image index {image_idx} out of range for dataset with {len(self.dataset)} items")
            
        ground_truth = self.dataset[image_idx]["ground_truth"]
        
        # Convert ground truth and predictions to mappings for easier lookup
        gt_map = {item["row"]: item["text"] for item in ground_truth}
        gt_size_map = {item["row"]: item["size"] for item in ground_truth}
        pred_map = {item["row"]: item["text"] for item in model_response}
        
        # Evaluate each row
        results = []
        total_correct_chars = 0
        total_chars = 0
        
        # Track accuracy by font size
        by_font_size = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for row_num in sorted(set(gt_map.keys()) | set(pred_map.keys())):
            gt_text = gt_map.get(row_num, "")
            pred_text = pred_map.get(row_num, "")
            font_size = gt_size_map.get(row_num, 0)
            
            row_result = self.evaluate_row(gt_text, pred_text)
            row_result["row"] = row_num
            row_result["font_size"] = font_size
            results.append(row_result)
            
            total_correct_chars += row_result["correct_chars"]
            total_chars += row_result["total_chars"]
            
            # Track by font size
            by_font_size[font_size]["correct"] += row_result["correct_chars"]
            by_font_size[font_size]["total"] += row_result["total_chars"]
        
        # Calculate overall metrics for this image
        total_rows = len(ground_truth)
        rows_attempted = len(model_response)
        rows_matched = sum(1 for r in results if r["exact_match"])
        
        # Calculate accuracy by font size for this image
        size_accuracies = {
            size: metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0 
            for size, metrics in by_font_size.items()
        }
        
        return {
            "image_path": self.dataset[image_idx]["image_path"],
            "metadata": self.dataset[image_idx]["metadata"],
            "row_results": results,
            "rows_matched": rows_matched,
            "rows_attempted": rows_attempted,
            "total_rows": total_rows,
            "row_accuracy": rows_matched / total_rows if total_rows > 0 else 0,
            "char_accuracy": total_correct_chars / total_chars if total_chars > 0 else 0,
            "accuracy_by_size": size_accuracies
        }
        
    def evaluate_model(self, model_responses):
        """
        Evaluate model responses for the entire dataset.
        
        Args:
            model_responses: List of model responses, one per image.
                Each response is a list of dicts with format [{row: int, text: str}].
            
        Returns:
            dict: Overall evaluation metrics.
        """
        if len(model_responses) != len(self.dataset):
            raise ValueError(f"Expected {len(self.dataset)} model responses, got {len(model_responses)}")
            
        # Evaluate each image
        image_results = []
        for i, response in enumerate(model_responses):
            image_result = self.evaluate_image(i, response)
            image_results.append(image_result)
        
        # Calculate overall metrics
        total_rows = sum(r["total_rows"] for r in image_results)
        total_rows_matched = sum(r["rows_matched"] for r in image_results)
        total_chars = sum(sum(row["total_chars"] for row in r["row_results"]) for r in image_results)
        total_chars_correct = sum(sum(row["correct_chars"] for row in r["row_results"]) for r in image_results)
        
        # Group results by metadata properties for detailed analysis
        by_font = defaultdict(list)
        by_font_size = defaultdict(lambda: {"correct": 0, "total": 0})
        by_size_range = defaultdict(list)
        
        # New: Track accuracy by font size AND font
        by_font_size_and_font = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0}))
        
        for r in image_results:
            font_name = r["metadata"]["font"]
            by_font[font_name].append(r["char_accuracy"])
            
            # Group by font sizes range - use min/max of font_sizes
            if 'font_sizes' in r['metadata']:
                size_range = f"{min(r['metadata']['font_sizes'])}-{max(r['metadata']['font_sizes'])}"
                by_size_range[size_range].append(r["char_accuracy"])
            
            # Collect accuracy data by individual font size
            for row in r["row_results"]:
                font_size = row.get("font_size", 0)
                if font_size > 0:
                    by_font_size[font_size]["correct"] += row["correct_chars"]
                    by_font_size[font_size]["total"] += row["total_chars"]
                    
                    # Also track by both font size and font type
                    by_font_size_and_font[font_size][font_name]["correct"] += row["correct_chars"]
                    by_font_size_and_font[font_size][font_name]["total"] += row["total_chars"]
        
        # Calculate average accuracy for each group
        font_accuracies = {font: statistics.mean(accs) for font, accs in by_font.items()}
        size_range_accuracies = {size_range: statistics.mean(accs) for size_range, accs in by_size_range.items()}
        
        # Calculate accuracy by specific font size
        font_size_accuracies = {
            size: metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0
            for size, metrics in by_font_size.items()
        }
        
        # New: Calculate accuracy by font size and font type
        font_size_and_font_accuracies = {}
        for size, fonts in by_font_size_and_font.items():
            font_size_and_font_accuracies[str(size)] = {}
            for font, metrics in fonts.items():
                font_size_and_font_accuracies[str(size)][font] = (
                    metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0
                )
        
        return {
            "overall_row_accuracy": total_rows_matched / total_rows if total_rows > 0 else 0,
            "overall_char_accuracy": total_chars_correct / total_chars if total_chars > 0 else 0,
            "total_images": len(image_results),
            "total_rows": total_rows,
            "total_rows_matched": total_rows_matched,
            "total_chars": total_chars,
            "total_chars_correct": total_chars_correct,
            "accuracy_by_font": font_accuracies,
            "accuracy_by_size_range": size_range_accuracies,
            "accuracy_by_font_size": font_size_accuracies,
            "accuracy_by_font_size_and_font": font_size_and_font_accuracies,
            "image_results": image_results
        }
    
    def save_evaluation(self, evaluation, output_path="evaluation_results.json"):
        """Save evaluation results to a JSON file."""
        with open(output_path, 'w') as f:
            json.dump(evaluation, f, indent=2)


if __name__ == "__main__":
    # Example usage with mock model responses
    evaluator = VisionModelEvaluator()
    
    # Create mock model responses - in a real scenario, these would come from the model
    mock_responses = []
    for item in evaluator.dataset:
        # For this example, we'll assume the model gets some rows correct, some partially correct
        mock_response = []
        for gt_row in item["ground_truth"]:
            row_num = gt_row["row"]
            true_text = gt_row["text"]
            font_size = gt_row["size"]
            
            # Simulate different levels of accuracy based on font size
            # Larger font sizes are easier to read
            if font_size >= 36:
                # Model gets large text exactly right
                pred_text = true_text
            elif font_size >= 18:
                # Model makes some errors in medium text
                # Simulate by replacing 20% of characters with errors
                chars = list(true_text)
                error_positions = sorted(set([int(i) for i in range(len(chars)) if i % 5 == 0]))
                for pos in error_positions:
                    if pos < len(chars):
                        chars[pos] = 'X'  # Replace with a wrong character
                pred_text = ''.join(chars)
            else:
                # Model struggles with small text, missing characters or getting them wrong
                # Simulate by getting only first half right
                half_len = len(true_text) // 2
                pred_text = true_text[:half_len] + 'X' * (len(true_text) - half_len)
            
            mock_response.append({"row": row_num, "text": pred_text})
        
        mock_responses.append(mock_response)
    
    # Evaluate the mock model
    results = evaluator.evaluate_model(mock_responses)
    
    # Print summary results
    print(f"Overall character accuracy: {results['overall_char_accuracy']:.2%}")
    print(f"Overall row accuracy: {results['overall_row_accuracy']:.2%}")
    
    print("\nAccuracy by font:")
    for font, acc in sorted(results['accuracy_by_font'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {font}: {acc:.2%}")
    
    print("\nAccuracy by font size:")
    for size, acc in sorted(results['accuracy_by_font_size'].items(), key=lambda x: int(x[0]), reverse=True):
        print(f"  {size:3d}pt: {acc:.2%}")
    
    # Save detailed results
    evaluator.save_evaluation(results)
    print(f"\nDetailed evaluation saved to evaluation_results.json")