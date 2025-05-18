import argparse
import os
import json
from datetime import datetime

from image_generator import EyeChartGenerator
from dataset_creator import DatasetCreator
from evaluator import VisionModelEvaluator
from model_runner import ModelRunner

def parse_args():
    parser = argparse.ArgumentParser(description="AI Spy - Vision model eye chart benchmark")
    
    # Dataset generation arguments
    parser.add_argument("--generate", action="store_true", help="Generate new test images and dataset")
    parser.add_argument("--fonts", type=int, default=None, help="Number of fonts to use (default: all)")
    parser.add_argument("--images-per-font", type=int, default=3, help="Number of images per font (default: 3)")
    parser.add_argument("--output-dir", type=str, default="test_images", help="Directory for test images")
    parser.add_argument("--dataset", type=str, default="dataset.json", help="Path to dataset file")
    
    # Evaluation arguments
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation")
    parser.add_argument("--model", type=str, choices=[
        "mock", 
        "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
        "claude-3-5-sonnet", "claude-3-5-sonnet-v2", "claude-3-5-haiku",
        "claude-3-7-sonnet"
    ], default="mock", help="Model to evaluate (default: mock)")
    parser.add_argument("--model-responses", type=str, default=None, 
                      help="Path to saved model responses JSON (default: None = run the model)")
    parser.add_argument("--api-key", type=str, default=None, 
                      help="API key for real models (default: uses ANTHROPIC_API_KEY environment variable)")
    parser.add_argument("--responses", type=str, default=None, 
                      help="Path to save model responses (default: data/responses/model_name_responses.json)")
    parser.add_argument("--results", type=str, default=None, 
                      help="Path to save evaluation results (default: data/results/model_name_results.json)")
    
    # Compare models
    parser.add_argument("--compare", nargs="+", 
                      help="Compare multiple models by specifying their result files")
    
    return parser.parse_args()

def generate_mock_responses(dataset_path):
    """
    Generate mock model responses for testing the evaluator.
    
    Args:
        dataset_path: Path to the dataset JSON file.
        
    Returns:
        List of mock responses, one per image.
    """
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    mock_responses = []
    for item in dataset:
        # For testing, we'll assume the model gets some rows correct, some partially correct
        mock_response = []
        for gt_row in item["ground_truth"]:
            row_num = gt_row["row"]  # Already 0-indexed
            true_text = gt_row["text"]
            font_size = gt_row["size"]
            
            # Simulate different levels of accuracy based on font size
            # Larger font sizes are easier to read
            if font_size >= 36:
                # Model gets large text exactly right
                pred_text = true_text
            elif font_size >= 18:
                # Model makes some errors in medium text
                chars = list(true_text)
                error_positions = [i for i in range(len(chars)) if i % 5 == 0]
                for pos in error_positions:
                    if pos < len(chars):
                        chars[pos] = 'X'  # Replace with a wrong character
                pred_text = ''.join(chars)
            else:
                # Model struggles with smaller text
                half_len = len(true_text) // 2
                pred_text = true_text[:half_len] + 'X' * (len(true_text) - half_len)
            
            mock_response.append({"row": row_num, "text": pred_text})
        
        mock_responses.append(mock_response)
    
    return mock_responses

def print_summary(results, model_name="Model"):
    """Print a summary of evaluation results."""
    print("\n" + "="*50)
    print(f"AI SPY VISION BENCHMARK RESULTS: {model_name}")
    print("="*50)
    
    print(f"\nOverall Results:")
    print(f"  Images tested: {results['total_images']}")
    print(f"  Character accuracy: {results['overall_char_accuracy']:.2%}")
    print(f"  Row accuracy: {results['overall_row_accuracy']:.2%}")
    
    print("\nAccuracy by Font:")
    for font, acc in sorted(results['accuracy_by_font'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {font}: {acc:.2%}")
    
    print("\nAccuracy by Font Size Range:")
    for size_range, acc in sorted(results['accuracy_by_size_range'].items()):
        print(f"  {size_range}: {acc:.2%}")
    
    print("\nAccuracy by Exact Font Size:")
    for size, acc in sorted(results['accuracy_by_font_size'].items(), key=lambda x: int(x[0]), reverse=True):
        print(f"  {size:3d}pt: {acc:.2%}")
    
    # Examples of worst-performing images
    print("\nWorst Performing Images:")
    image_accuracies = [(i, r["char_accuracy"]) for i, r in enumerate(results["image_results"])]
    image_accuracies.sort(key=lambda x: x[1])
    
    for idx, acc in image_accuracies[:3]:
        img_result = results["image_results"][idx]
        print(f"  {img_result['image_path']}: {acc:.2%} accuracy")
        print(f"    Font: {img_result['metadata']['font']}")
        if 'font_sizes' in img_result['metadata']:
            sizes = img_result['metadata']['font_sizes']
            print(f"    Font sizes: {min(sizes)}-{max(sizes)}pt")
    
    print("\n" + "="*50)

def compare_models(result_files):
    """Compare results from multiple models."""
    results = []
    for file_path in result_files:
        if not os.path.exists(file_path):
            print(f"Warning: Result file {file_path} not found, skipping")
            continue
            
        with open(file_path, 'r') as f:
            result = json.load(f)
            model_name = os.path.basename(file_path).replace("_results.json", "")
            results.append((model_name, result))
    
    if not results:
        print("No valid result files found for comparison")
        return
    
    print("\n" + "="*50)
    print("MODEL COMPARISON")
    print("="*50)
    
    # Overall comparison
    print("\nOverall Character Accuracy:")
    for model_name, result in sorted(results, key=lambda x: x[1]["overall_char_accuracy"], reverse=True):
        print(f"  {model_name}: {result['overall_char_accuracy']:.2%}")
    
    print("\nOverall Row Accuracy:")
    for model_name, result in sorted(results, key=lambda x: x[1]["overall_row_accuracy"], reverse=True):
        print(f"  {model_name}: {result['overall_row_accuracy']:.2%}")
    
    # Comparison by font size
    print("\nAccuracy by Font Size:")
    size_comparison = {}
    
    # Collect all font sizes across all models
    all_sizes = set()
    for _, result in results:
        all_sizes.update(result["accuracy_by_font_size"].keys())
    
    # Format comparison for each font size
    for size in sorted([int(s) for s in all_sizes], reverse=True):
        size_str = str(size)
        size_comparison[size_str] = []
        
        for model_name, result in results:
            accuracy = result["accuracy_by_font_size"].get(size_str, 0)
            size_comparison[size_str].append((model_name, accuracy))
    
    # Print comparison for each font size
    for size, model_accuracies in sorted(size_comparison.items(), key=lambda x: int(x[0]), reverse=True):
        print(f"\n  Font Size {size}pt:")
        for model_name, accuracy in sorted(model_accuracies, key=lambda x: x[1], reverse=True):
            print(f"    {model_name}: {accuracy:.2%}")
    
    print("\n" + "="*50)

def main():
    args = parse_args()
    
    # Generate dataset if requested
    if args.generate:
        print("Generating test images...")
        
        # Clean test images directory if it exists
        if os.path.exists(args.output_dir):
            print(f"Cleaning existing images in {args.output_dir}...")
            for root, dirs, files in os.walk(args.output_dir, topdown=False):
                for file in files:
                    if file.endswith('.png'):
                        os.remove(os.path.join(root, file))
        
        generator = EyeChartGenerator(output_dir=args.output_dir)
        
        print("Creating dataset...")
        creator = DatasetCreator(output_file=args.dataset)
        dataset = creator.create_dataset(
            num_fonts=args.fonts, 
            num_images_per_font=args.images_per_font
        )
        
        # Get a count of actual image files generated by font
        image_count_by_font = {}
        for entry in dataset:
            font = entry["metadata"]["font"]
            image_path = entry["image_path"]
            
            if os.path.exists(image_path):
                if font not in image_count_by_font:
                    image_count_by_font[font] = []
                
                if image_path not in image_count_by_font[font]:
                    image_count_by_font[font].append(image_path)
        
        # Calculate total unique images
        total_images = sum(len(images) for images in image_count_by_font.values())
        
        print(f"\nCreated dataset with {len(dataset)} entries and {total_images} unique image files:")
        for font, images in image_count_by_font.items():
            print(f"  {font}: {len(images)} image(s)")
            
        print(f"\nDataset saved to {args.dataset}")
    
    # Compare models if requested
    if args.compare:
        compare_models(args.compare)
        return
    
    # Evaluate model if requested
    if args.evaluate:
        if not os.path.exists(args.dataset):
            print(f"Error: Dataset file {args.dataset} not found. Run with --generate first.")
            return
        
        # Create responses and results directories if they don't exist
        os.makedirs("data/responses", exist_ok=True)
        os.makedirs("data/results", exist_ok=True)
        
        # Set default responses and results paths if not provided
        if not args.responses:
            args.responses = os.path.join("data/responses", f"{args.model}_responses.json")
            
        if not args.results:
            args.results = os.path.join("data/results", f"{args.model}_results.json")
        
        print(f"Evaluating model: {args.model}")
        evaluator = VisionModelEvaluator(dataset_path=args.dataset)
        
        # Get model responses
        if args.model_responses and os.path.exists(args.model_responses):
            # Load saved responses from specified path
            print(f"Loading saved responses from {args.model_responses}")
            with open(args.model_responses, 'r') as f:
                model_responses = json.load(f)
        elif os.path.exists(args.responses):
            # Try using the responses path directly
            print(f"Loading saved responses from {args.responses}")
            with open(args.responses, 'r') as f:
                model_responses = json.load(f)
        elif args.model == "mock":
            # Generate mock responses
            print("Generating mock responses")
            model_responses = generate_mock_responses(args.dataset)
        else:
            # Run real model
            print(f"Running {args.model} model on dataset...")
            
            # Map model choice to Anthropic model ID
            model_map = {
                # Claude 3 family
                "claude-3-opus": "claude-3-opus-20240229",
                "claude-3-sonnet": "claude-3-sonnet-20240229",
                "claude-3-haiku": "claude-3-haiku-20240307",
                
                # Claude 3.5 family
                "claude-3-5-sonnet": "claude-3-5-sonnet-20240620",
                "claude-3-5-sonnet-v2": "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku": "claude-3-5-haiku-20241022",
                
                # Claude 3.7 family
                "claude-3-7-sonnet": "claude-3-7-sonnet-20250219"
            }
            
            if args.model not in model_map:
                print(f"Error: Unknown model '{args.model}'")
                return
            
            model_id = model_map[args.model]
            
            # Check for API key
            if not args.api_key and not os.environ.get("ANTHROPIC_API_KEY"):
                print("Error: API key must be provided via --api-key or ANTHROPIC_API_KEY environment variable")
                return
            
            # Run model
            runner = ModelRunner(model_name=model_id, api_key=args.api_key)
            model_responses = runner.run_on_dataset(args.dataset)
            
            # Save responses to the specified path
            with open(args.responses, 'w') as f:
                json.dump(model_responses, f, indent=2)
            print(f"Saved model responses to {args.responses}")
        
        # Run evaluation
        print("Evaluating responses...")
        results = evaluator.evaluate_model(model_responses)
        
        # Save results
        evaluator.save_evaluation(results, output_path=args.results)
        print(f"Detailed evaluation saved to {args.results}")
        
        # Print summary
        print_summary(results, model_name=args.model.upper())

if __name__ == "__main__":
    main()