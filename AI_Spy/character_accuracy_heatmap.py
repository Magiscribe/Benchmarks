#!/usr/bin/env python3
"""
Creates a heatmap visualization of character accuracy across models and fonts for the AI Spy benchmark.
"""

import os
import json
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a heatmap visualization of character accuracy across models and fonts")
    
    parser.add_argument("--results-dir", type=str, default="data/results",
                       help="Directory containing result JSON files (must end with _results.json)")
    parser.add_argument("--output-dir", type=str, default="data/visualizations",
                       help="Directory to save the heatmap visualization")
    parser.add_argument("--dpi", type=int, default=300,
                       help="DPI for saved figures (default: 300)")
    parser.add_argument("--figsize", type=str, default="12,10",
                       help="Figure size in inches as width,height (default: 12,10)")
    parser.add_argument("--title", type=str, default="AI Spy Character Accuracy by Font and Model",
                       help="Title for the heatmap visualization")
    
    return parser.parse_args()

def load_results(results_dir):
    """Load results from all JSON files in the specified directory."""
    result_files = glob.glob(os.path.join(results_dir, "*_results.json"))
    if not result_files:
        raise ValueError(f"No result files found in {results_dir}")
    
    results = []
    for file_path in result_files:
        # Extract model name from filename
        model_name = os.path.basename(file_path).replace("_results.json", "")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                results.append((model_name, data))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return results

def generate_character_accuracy_heatmap(results, output_dir, figsize, dpi, title):
    """
    Generate a heatmap visualization of character accuracy across models and fonts.
    
    Args:
        results: List of tuples (model_name, result_data)
        output_dir: Directory to save the visualization
        figsize: Tuple of (width, height) for the figure
        dpi: DPI for the saved figure
        title: Title for the visualization
    
    Returns:
        str: Path to the saved heatmap image
    """
    # Extract model names and fonts
    model_names = [model_name for model_name, _ in results]
    
    # Determine all unique fonts across all results
    all_fonts = set()
    for _, result in results:
        all_fonts.update(result["accuracy_by_font"].keys())
    
    fonts = sorted(all_fonts)
    
    # Create data matrix for heatmap
    data = np.zeros((len(model_names), len(fonts)))
    
    # Fill data matrix with character accuracy values
    for i, (_, result) in enumerate(results):
        for j, font in enumerate(fonts):
            if font in result["accuracy_by_font"]:
                data[i, j] = result["accuracy_by_font"][font]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Generate heatmap
    sns.heatmap(data, annot=True, fmt=".2%", cmap="YlGnBu", vmin=0, vmax=1,
                xticklabels=fonts, yticklabels=model_names, cbar_kws={'label': 'Character Accuracy'})
    
    # Configure plot
    plt.title(title)
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = os.path.join(output_dir, f"character_accuracy_heatmap_{timestamp}.png")
    plt.savefig(fig_path, dpi=dpi)
    print(f"Character accuracy heatmap saved to {fig_path}")
    
    return fig_path

def main():
    args = parse_args()
    
    # Parse figsize
    try:
        figsize = tuple(map(float, args.figsize.split(',')))
        if len(figsize) != 2:
            raise ValueError()
    except:
        print(f"Invalid figsize: {args.figsize}, using default (12,10)")
        figsize = (12, 10)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load results
    results = load_results(args.results_dir)
    print(f"Loaded results for {len(results)} models")
    
    # Generate heatmap
    heatmap_path = generate_character_accuracy_heatmap(
        results, args.output_dir, figsize, args.dpi, args.title
    )
    
    print(f"Heatmap visualization created: {heatmap_path}")

if __name__ == "__main__":
    main()