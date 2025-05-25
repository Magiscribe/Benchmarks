import argparse
import os
import sys
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

from utils.asset_generator import CoordinateGridGenerator
from utils.dataset_creator import DatasetCreator
from utils.model_evaluator import CoordinateGridEvaluator
from test_config import (
    IMAGE_WIDTH, IMAGE_HEIGHT, SQUARE_SIZE, NUM_SQUARES, 
    MIN_DISTANCE_BETWEEN_SQUARES, IMAGES_PER_SET, OUTPUT_DIR, 
    DATASET_FILE, DEFAULT_MODEL, RESPONSES_DIR
)

def parse_args():
    parser = argparse.ArgumentParser(description="LLM Coordinate Grid Test - Vision model benchmark for spatial reasoning")
    
    # Dataset generation arguments
    parser.add_argument("--generate", action="store_true", help="Generate new test images and dataset")
    parser.add_argument("--num-images", type=int, default=IMAGES_PER_SET, 
                      help=f"Number of test images to generate (default: {IMAGES_PER_SET})")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, 
                      help=f"Directory for test images (default: {OUTPUT_DIR})")
    parser.add_argument("--dataset", type=str, default=DATASET_FILE, 
                      help=f"Path to dataset file (default: {DATASET_FILE})")
    
    # Image configuration arguments
    parser.add_argument("--image-width", type=int, default=IMAGE_WIDTH,
                      help=f"Width of generated images (default: {IMAGE_WIDTH})")    
    parser.add_argument("--image-height", type=int, default=IMAGE_HEIGHT,
                      help=f"Height of generated images (default: {IMAGE_HEIGHT})")
    parser.add_argument("--square-size", type=int, default=SQUARE_SIZE,
                      help=f"Size of squares in pixels (default: {SQUARE_SIZE})")
    parser.add_argument("--num-squares", type=int, default=NUM_SQUARES,
                      help=f"Number of squares per image (default: {NUM_SQUARES})")
    parser.add_argument("--min-distance", type=int, default=MIN_DISTANCE_BETWEEN_SQUARES,
                      help=f"Minimum distance between square centers in both X and Y directions (default: {MIN_DISTANCE_BETWEEN_SQUARES})")
    
    # Model evaluation arguments
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation on existing model responses")
    parser.add_argument("--run-model", action="store_true", help="Run model inference on the dataset")
    parser.add_argument("--model", type=str, choices=AVAILABLE_MODELS,
        default=DEFAULT_MODEL, 
        help=f"Model to evaluate (default: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", type=str, 
        help="API key for the model (can also use environment variables)")
    parser.add_argument("--tolerance", type=int, default=10,
        help="Maximum pixel distance for correct coordinate prediction (default: 10)")
    parser.add_argument("--responses-dir", type=str, default=RESPONSES_DIR,
        help=f"Directory containing model response files (default: {RESPONSES_DIR})")
    parser.add_argument("--model-responses", type=str,
        help="Path to specific model responses file to load")
    
    return parser.parse_args()

def print_dataset_summary(dataset, stats):
    """Print a summary of the generated dataset."""
    print("\n" + "="*60)
    print("LLM COORDINATE GRID TEST - DATASET SUMMARY")
    print("="*60)
    
    print(f"\nDataset Statistics:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Total squares: {stats['total_squares']}")
    print(f"  Squares per image: {stats['squares_per_image']}")
    
    print(f"\nCoordinate Ranges:")
    coord_ranges = stats['coordinate_ranges']
    print(f"  X coordinates: {coord_ranges['x_min']} - {coord_ranges['x_max']}")
    print(f"  Y coordinates: {coord_ranges['y_min']} - {coord_ranges['y_max']}")
    
    print(f"\nSample Images:")
    for i, entry in enumerate(dataset[:3]):  # Show first 3 images
        print(f"  {entry['image_path']}:")
        squares = entry['ground_truth']
        coords_str = ", ".join([f"({sq['x']}, {sq['y']})" for sq in squares])
        print(f"    Squares (left to right): {coords_str}")
    
    if len(dataset) > 3:
        print(f"  ... and {len(dataset) - 3} more images")
    
    print("\n" + "="*60)

def main():
    args = parse_args()
    
    # Generate dataset if requested
    if args.generate:
        print("Generating coordinate grid test images...")
        
        # Clean test images directory if it exists
        if os.path.exists(args.output_dir):
            print(f"Cleaning existing images in {args.output_dir}...")
            for file in os.listdir(args.output_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(args.output_dir, file))
        
        print("Creating dataset...")
        creator = DatasetCreator(output_file=args.dataset)
        dataset = creator.create_dataset(
            num_images=args.num_images,
            image_width=args.image_width,
            image_height=args.image_height,
            square_size=args.square_size,
            num_squares=args.num_squares,
            min_distance=args.min_distance,
            output_dir=args.output_dir
        )
        
        # Get and print dataset statistics
        stats = creator.get_dataset_stats(dataset)
        print_dataset_summary(dataset, stats)
          # Verify image files were created
        image_count = len([f for f in os.listdir(args.output_dir) if f.endswith('.png')])
        print(f"\nVerification: {image_count} image file(s) created in {args.output_dir}")
        print(f"Dataset saved to {args.dataset}")
    
    # Run model inference
    if args.run_model:
        print(f"\nRunning model inference with {args.model}...")
        
        # Check if dataset exists
        if not os.path.exists(args.dataset):
            print(f"Error: Dataset file {args.dataset} does not exist.")
            print("Run with --generate first to create a dataset.")
            sys.exit(1)
        
        # Get model ID from config
        if args.model not in MODELS:
            print(f"Error: Unknown model '{args.model}'")
            print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
            sys.exit(1)
        
        model_id = MODELS[args.model]
        
        # Create responses directory if it doesn't exist
        os.makedirs(args.responses_dir, exist_ok=True)
        
        # Set default response file path
        responses_file = os.path.join(args.responses_dir, f"{args.model}_responses.json")
          # Check if responses already exist
        choice = None
        if os.path.exists(responses_file):
            print(f"\nExisting responses found for {args.model} at {responses_file}")
            choice = input("Do you want to (r)e-run the model or (s)kip? [r/s]: ").lower().strip()
            
            if choice == 's' or choice == 'skip':
                print("Skipping model inference.")
            elif choice == 'r' or choice == 're-run' or choice == 'rerun':
                print(f"Re-running {args.model} model on dataset...")
                # Continue with model run
            else:
                print("Invalid choice. Please enter 'r' for re-run or 's' for skip.")
                sys.exit(1)
        
        if not os.path.exists(responses_file) or choice in ['r', 're-run', 'rerun']:
            # Get system messages directory for this test
            system_messages_dir = os.path.join(os.path.dirname(__file__), "system_messages")
            
            # Run model
            print(f"Running {model_id} on dataset...")
            runner = ModelRunner(model_name=model_id, api_key=args.api_key, system_messages_dir=system_messages_dir)
            model_responses = runner.run_on_dataset(args.dataset)
            
            # Save responses
            with open(responses_file, 'w') as f:
                import json
                json.dump(model_responses, f, indent=2)
            print(f"Saved model responses to {responses_file}")
      # Evaluate model responses
    if args.evaluate:
        print(f"\nRunning model evaluation for {args.model}...")
        
        # Check if dataset exists
        if not os.path.exists(args.dataset):
            print(f"Error: Dataset file {args.dataset} does not exist.")
            print("Run with --generate first to create a dataset.")
            sys.exit(1)
        
        # Create responses directory if it doesn't exist
        os.makedirs(args.responses_dir, exist_ok=True)
        
        # Set response file path for the specified model
        responses_file = os.path.join(args.responses_dir, f"{args.model}_responses.json")
          # Check if responses already exist for this model
        need_to_run_model = True
        if os.path.exists(responses_file):
            print(f"Found existing responses for {args.model}")
            choice = input("Do you want to (r)e-run the model or (a)nalyze existing data? [r/a]: ").lower().strip()
            
            if choice == 'a' or choice == 'analyze':
                print("Analyzing existing responses.")
                need_to_run_model = False
            elif choice == 'r' or choice == 're-run' or choice == 'rerun':
                print(f"Re-running {args.model} model...")
                need_to_run_model = True
            else:
                print("Invalid choice. Please enter 'r' for re-run or 'a' for analyze.")
                return
        
        # Run model inference if needed
        if need_to_run_model:
            # Get model ID from config
            if args.model not in MODELS:
                print(f"Error: Unknown model '{args.model}'")
                print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
                sys.exit(1)
            
            model_id = MODELS[args.model]
            
            # Get system messages directory for this test
            system_messages_dir = os.path.join(os.path.dirname(__file__), "system_messages")
            
            # Run model
            print(f"Running {model_id} on dataset...")
            runner = ModelRunner(model_name=model_id, api_key=args.api_key, system_messages_dir=system_messages_dir)
            model_responses = runner.run_on_dataset(args.dataset)
            
            # Save responses
            with open(responses_file, 'w') as f:
                import json
                json.dump(model_responses, f, indent=2)
            print(f"Saved model responses to {responses_file}")
        
        # Load and evaluate the model responses
        print(f"\nEvaluating {args.model}...")
        
        # Load model responses
        import json
        with open(responses_file, 'r') as f:
            model_responses = json.load(f)
        
        # Load evaluator and evaluate
        evaluator = CoordinateGridEvaluator(dataset_path=args.dataset)
        evaluation = evaluator.evaluate_model(model_responses, tolerance=args.tolerance)        # Print evaluation summary
        print(f"  Overall accuracy: {evaluation['overall_accuracy']:.3f}")
        print(f"  Average distance: {evaluation['average_distance']:.1f} pixels")
        print(f"  Squares correct: {evaluation['total_squares_correct']}/{evaluation['total_squares']}")
        print(f"  Images evaluated: {evaluation['total_images']}")
        print(f"  Tolerance: {evaluation['tolerance_used']} pixels")
          # Automatically synthesize results
        print("\nSynthesizing model results...")
        from utils.synthesize_model_results import main as synthesize_main
        try:
            synthesize_main()
        except Exception as e:
            print(f"Warning: Could not synthesize results - {e}")

if __name__ == "__main__":
    main()
