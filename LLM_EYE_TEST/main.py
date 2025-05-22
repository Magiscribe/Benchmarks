import argparse
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import config

# Load environment variables from .env file
load_dotenv()

from image_generator import EyeChartGenerator
from dataset_creator import DatasetCreator
from evaluator import VisionModelEvaluator
from model_runner import ModelRunner

def parse_args():
    parser = argparse.ArgumentParser(description="LLM Eye Test - Vision model benchmark")
    
    # Dataset generation arguments
    parser.add_argument("--generate", action="store_true", help="Generate new test images and dataset")
    parser.add_argument("--fonts", type=int, default=None, help="Number of fonts to use (default: all)")
    parser.add_argument("--images-per-font", type=int, default=int(os.getenv('IMAGES_PER_FONT', 3)), 
                      help=f"Number of images per font (default: {os.getenv('IMAGES_PER_FONT', 3)})")
    parser.add_argument("--output-dir", type=str, default=os.getenv('OUTPUT_DIR', 'test_images'), 
                      help=f"Directory for test images (default: {os.getenv('OUTPUT_DIR', 'test_images')})")
    parser.add_argument("--dataset", type=str, default=os.getenv('DATASET_FILE', 'dataset.json'), 
                      help=f"Path to dataset file (default: {os.getenv('DATASET_FILE', 'dataset.json')})")
    
    # Evaluation arguments
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation")
    parser.add_argument("--model", type=str, choices=config.AVAILABLE_MODELS,
        default=os.getenv('DEFAULT_MODEL', 'claude-3-7-sonnet'), 
        help=f"Model to evaluate (default: {os.getenv('DEFAULT_MODEL', 'claude-3-7-sonnet')})")
    parser.add_argument("--model-responses", type=str, default=None, 
                      help="Path to saved model responses JSON (default: None = run the model)")
    parser.add_argument("--api-key", type=str, default=None, 
                      help="API key for models (default: uses appropriate API key from .env based on model provider)")
    parser.add_argument("--responses", type=str, default=None, 
                      help=f"Path to save model responses (default: {os.getenv('RESPONSES_DIR', 'data/responses')}/model_name_responses.json)")
    parser.add_argument("--results", type=str, default=None, 
                      help=f"Path to save evaluation results (default: {os.getenv('RESULTS_DIR', 'data/results')}/model_name_results.json)")
    
    return parser.parse_args()


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
        else:
            # Run real model
            print(f"Running {args.model} model on dataset...")
            
            # Get model ID from config
            if args.model not in config.MODELS:
                print(f"Error: Unknown model '{args.model}'")
                return
            
            model_id = config.MODELS[args.model]
            
            # API key will be handled by ModelRunner class
            
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
        
        # Automatically run generate_model_results.py after evaluation
        print("\nGenerating consolidated model results...")
        import subprocess
        subprocess.run(["python", "generate_model_results.py"])

if __name__ == "__main__":
    main()