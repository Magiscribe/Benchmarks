#!/usr/bin/env python3
"""
Run all supported models on the AI Spy benchmark and generate a comparison report.
"""

import os
import json
import argparse
import subprocess
import time
from datetime import datetime
import matplotlib.pyplot as plt

# All supported models
ALL_MODELS = [
    "mock",
    "claude-3-opus", 
    "claude-3-sonnet", 
    "claude-3-haiku",
    "claude-3-5-sonnet", 
    "claude-3-5-sonnet-v2", 
    "claude-3-5-haiku",
    "claude-3-7-sonnet"
]

def parse_args():
    parser = argparse.ArgumentParser(description="Run all supported models on the AI Spy benchmark")
    
    parser.add_argument("--models", nargs="+", choices=ALL_MODELS, default=None,
                       help="Specific models to run (default: all models)")
    parser.add_argument("--generate", action="store_true", 
                       help="Generate a new dataset before running models")
    parser.add_argument("--images-per-font", type=int, default=1,
                       help="Number of images per font when generating dataset (default: 1)")
    parser.add_argument("--dataset", type=str, default="dataset.json",
                       help="Path to dataset file (default: dataset.json)")
    parser.add_argument("--output-dir", type=str, default="data",
                       help="Directory to save results (default: data)")
    parser.add_argument("--skip-existing", action="store_true",
                       help="Skip models that already have result files")
    parser.add_argument("--api-key", type=str, default=None,
                       help="API key for Claude models (default: uses ANTHROPIC_API_KEY environment variable)")
    parser.add_argument("--delay", type=int, default=5,
                       help="Delay between model runs in seconds (default: 5)")
    parser.add_argument("--visualize", action="store_true",
                       help="Generate visualizations after running models")
    parser.add_argument("--vis-dpi", type=int, default=300,
                       help="DPI for visualizations (default: 300)")
    
    return parser.parse_args()

def run_model(model, dataset_path, output_dir, api_key=None):
    """Run a single model and save its results."""
    # Create responses and results directories if they don't exist
    responses_dir = os.path.join(output_dir, "responses")
    results_dir = os.path.join(output_dir, "results")
    os.makedirs(responses_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Construct output paths
    response_path = os.path.join(responses_dir, f"{model}_responses.json")
    result_path = os.path.join(results_dir, f"{model}_results.json")
    
    # Skip if results already exist and --skip-existing is set
    if args.skip_existing and os.path.exists(result_path):
        print(f"Skipping {model} - results already exist at {result_path}")
        return result_path
    
    # Build command
    cmd = ["python", "main.py", "--evaluate", "--model", model, "--dataset", dataset_path, "--responses", response_path, "--results", result_path]
    
    # Add API key if provided
    if api_key:
        cmd.extend(["--api-key", api_key])
    
    # Run the command
    print(f"\n{'='*50}")
    print(f"Running {model}...")
    print(f"{'='*50}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Completed {model}")
        return result_path
    except subprocess.CalledProcessError as e:
        print(f"Error running {model}: {e}")
        return None

def generate_dataset(args):
    """Generate a new dataset."""
    print(f"\n{'='*50}")
    print(f"Generating dataset...")
    print(f"{'='*50}")
    
    cmd = ["python", "main.py", "--generate", "--dataset", args.dataset, "--images-per-font", str(args.images_per_font)]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Dataset generated at {args.dataset}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating dataset: {e}")
        return False

def compare_models(result_files, output_dir):
    """Compare all successfully run models."""
    if len(result_files) <= 1:
        print("Not enough models to compare (need at least 2)")
        return
    
    print(f"\n{'='*50}")
    print(f"Comparing models...")
    print(f"{'='*50}")
    
    # Generate a timestamp for the comparison file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_path = os.path.join(output_dir, f"comparison_{timestamp}.txt")
    
    # Run the comparison command
    cmd = ["python", "main.py", "--compare"] + result_files
    
    try:
        # Capture output
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Save comparison results to file
        with open(comparison_path, 'w') as f:
            f.write(result.stdout)
        
        print(f"Comparison saved to {comparison_path}")
        
        # Also print to console
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error comparing models: {e}")
        
    return comparison_path

def generate_visualizations(result_files, output_dir, dpi=300):
    """Generate visualizations of the results."""
    if len(result_files) <= 1:
        print("Not enough models to visualize (need at least 2)")
        return
    
    print(f"\n{'='*50}")
    print(f"Generating visualizations...")
    print(f"{'='*50}")
    
    # Run visualizations script with the data-dir parameter
    cmd = ["python", "visualizations.py", "--data-dir", output_dir, "--dpi", str(dpi)]
    
    try:
        # Run visualization command
        subprocess.run(cmd, check=True)
        vis_dir = os.path.join(output_dir, "visualizations")
        print(f"Visualizations saved to {vis_dir}")
        return vis_dir
    except subprocess.CalledProcessError as e:
        print(f"Error generating visualizations: {e}")
        return None

def main():
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate dataset if requested
    if args.generate:
        if not generate_dataset(args):
            print("Failed to generate dataset. Exiting.")
            return
    
    # Determine which models to run
    models_to_run = args.models if args.models else ALL_MODELS
    
    # Check for mock-only run
    if args.api_key is None and os.environ.get("ANTHROPIC_API_KEY") is None and "mock" in models_to_run:
        non_mock_models = [m for m in models_to_run if m != "mock"]
        if non_mock_models:
            print(f"Warning: No API key provided. Will only run the mock model, skipping: {non_mock_models}")
            models_to_run = ["mock"]
    
    # Run each model
    successful_results = []
    for model in models_to_run:
        result_path = run_model(model, args.dataset, args.output_dir, args.api_key)
        if result_path:
            successful_results.append(result_path)
        
        # Add delay between runs (except after the last one)
        if model != models_to_run[-1] and args.delay > 0:
            print(f"Waiting {args.delay} seconds before the next model...")
            time.sleep(args.delay)
    
    # Compare all models that were run successfully
    if len(successful_results) > 1:
        compare_models(successful_results, args.output_dir)
        
        # Generate visualizations if requested
        if args.visualize:
            generate_visualizations(successful_results, args.output_dir, dpi=args.vis_dpi)
    elif len(successful_results) == 1:
        print(f"\nOnly one model was run successfully. No comparison or visualizations generated.")
    else:
        print(f"\nNo models were run successfully.")

if __name__ == "__main__":
    args = parse_args()
    main()