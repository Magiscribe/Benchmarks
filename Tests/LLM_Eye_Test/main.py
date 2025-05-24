import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add the Inference directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Inference'))

# Import shared model configuration from Inference
from available_models import AVAILABLE_MODELS, MODELS
from model_runner import ModelRunner

# Load environment variables from .env file in root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

from utils.image_generator import EyeChartGenerator
from utils.dataset_creator import DatasetCreator
from utils.model_evaluator import VisionModelEvaluator
from test_config import IMAGES_PER_FONT, OUTPUT_DIR, DATASET_FILE, DEFAULT_MODEL, RESPONSES_DIR

def parse_args():
    parser = argparse.ArgumentParser(description="LLM Eye Test - Vision model benchmark")
    
    # Dataset generation arguments
    parser.add_argument("--generate", action="store_true", help="Generate new test images and dataset")
    parser.add_argument("--fonts", type=int, default=None, help="Number of fonts to use (default: all)")
    parser.add_argument("--images-per-font", type=int, default=IMAGES_PER_FONT, 
                      help=f"Number of images per font (default: {IMAGES_PER_FONT})")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, 
                      help=f"Directory for test images (default: {OUTPUT_DIR})")
    parser.add_argument("--dataset", type=str, default=DATASET_FILE, 
                      help=f"Path to dataset file (default: {DATASET_FILE})")
    
    # Evaluation arguments
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation")
    parser.add_argument("--model", type=str, choices=AVAILABLE_MODELS,
        default=DEFAULT_MODEL, 
        help=f"Model to evaluate (default: {DEFAULT_MODEL})")
    parser.add_argument("--model-responses", type=str, default=None, 
                      help="Path to saved model responses JSON (default: None = run the model)")
    parser.add_argument("--api-key", type=str, default=None, 
                      help="API key for models (default: uses appropriate API key from .env based on model provider)")
    parser.add_argument("--responses", type=str, default=None, 
                      help=f"Path to save model responses (default: {RESPONSES_DIR}/model_name_responses.json)")
    
    return parser.parse_args()


def print_summary(results, model_name="Model"):
    """Print a summary of evaluation results."""
    print("\n" + "="*50)
    print(f"LLM EYE TEST BENCHMARK RESULTS: {model_name}")
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
        
        # Create responses directory if it doesn't exist
        os.makedirs(RESPONSES_DIR, exist_ok=True)
        
        # Set default responses path if not provided
        if not args.responses:
            args.responses = os.path.join(RESPONSES_DIR, f"{args.model}_responses.json")
        
        print(f"Evaluating model: {args.model}")
        evaluator = VisionModelEvaluator(dataset_path=args.dataset)
        
        # Check if responses already exist and ask user what to do
        model_responses = None
        if args.model_responses and os.path.exists(args.model_responses):
            # Load saved responses from specified path
            print(f"Loading saved responses from {args.model_responses}")
            with open(args.model_responses, 'r') as f:
                model_responses = json.load(f)
        elif os.path.exists(args.responses):
            # Responses exist for this model, ask user what to do
            print(f"\nExisting responses found for {args.model} at {args.responses}")
            choice = input("Do you want to (r)e-run the model or (a)nalyze existing data? [r/a]: ").lower().strip()
            
            if choice == 'a' or choice == 'analyze':
                print(f"Loading existing responses from {args.responses}")
                with open(args.responses, 'r') as f:
                    model_responses = json.load(f)
            elif choice == 'r' or choice == 're-run' or choice == 'rerun':
                print(f"Re-running {args.model} model on dataset...")
                model_responses = None  # Will trigger model run below
            else:
                print("Invalid choice. Please enter 'r' for re-run or 'a' for analyze.")
                return
        
        # Run model if we don't have responses loaded yet
        if model_responses is None:
            # Get model ID from config
            if args.model not in MODELS:
                print(f"Error: Unknown model '{args.model}'")
                return
            
            model_id = MODELS[args.model]
            
            # Get system messages directory for this test
            system_messages_dir = os.path.join(os.path.dirname(__file__), "system_messages")
            
            # Run model
            runner = ModelRunner(model_name=model_id, api_key=args.api_key, system_messages_dir=system_messages_dir)
            model_responses = runner.run_on_dataset(args.dataset)
            
            # Save responses to the specified path
            with open(args.responses, 'w') as f:
                json.dump(model_responses, f, indent=2)
            print(f"Saved model responses to {args.responses}")
        
        # Run evaluation
        print("Evaluating responses...")
        results = evaluator.evaluate_model(model_responses)
        
        # Print summary (no longer saving results to file)
        print_summary(results, model_name=args.model.upper())
        
        # Automatically run synthesize_model_results.py after evaluation
        print("\nGenerating consolidated model results...")
        import subprocess
        subprocess.run(["python", "utils/synthesize_model_results.py"])

if __name__ == "__main__":
    main()