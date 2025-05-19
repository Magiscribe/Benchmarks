#!/usr/bin/env python3
"""
Creates detailed heatmap visualizations of character accuracy across models, fonts, and font sizes
for the AI Spy benchmark.
"""

import os
import json
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Generate detailed heatmap visualizations of character accuracy")
    
    parser.add_argument("--results-dir", type=str, default="data/results",
                       help="Directory containing result JSON files (must end with _results.json)")
    parser.add_argument("--output-dir", type=str, default="data/visualizations",
                       help="Directory to save the heatmap visualizations")
    parser.add_argument("--dpi", type=int, default=300,
                       help="DPI for saved figures (default: 300)")
    parser.add_argument("--figsize", type=str, default="14,12",
                       help="Figure size in inches as width,height (default: 14,12)")
    parser.add_argument("--title", type=str, default="AI Spy Character Accuracy",
                       help="Base title for visualizations")
    
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

def generate_basic_heatmap(results, output_dir, figsize, dpi, title):
    """Generate a basic heatmap of character accuracy by model and font."""
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
    plt.title(f"{title}: By Model and Font")
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = os.path.join(output_dir, f"model_font_heatmap_{timestamp}.png")
    plt.savefig(fig_path, dpi=dpi)
    print(f"Model-Font heatmap saved to {fig_path}")
    
    return fig_path

def generate_font_size_heatmap(results, output_dir, figsize, dpi, title):
    """Generate a heatmap of character accuracy by model and font size."""
    # Extract model names
    model_names = [model_name for model_name, _ in results]
    
    # Determine all unique font sizes across all results
    all_sizes = set()
    for _, result in results:
        all_sizes.update(result["accuracy_by_font_size"].keys())
    
    # Convert to integers and sort
    font_sizes = sorted([int(size) for size in all_sizes])
    
    # Create data matrix for heatmap
    data = np.zeros((len(model_names), len(font_sizes)))
    
    # Fill data matrix with character accuracy values
    for i, (_, result) in enumerate(results):
        for j, size in enumerate(font_sizes):
            size_str = str(size)
            if size_str in result["accuracy_by_font_size"]:
                data[i, j] = result["accuracy_by_font_size"][size_str]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Generate heatmap
    sns.heatmap(data, annot=True, fmt=".2%", cmap="YlGnBu", vmin=0, vmax=1,
                xticklabels=[f"{size}pt" for size in font_sizes], yticklabels=model_names, 
                cbar_kws={'label': 'Character Accuracy'})
    
    # Configure plot
    plt.title(f"{title}: By Model and Font Size")
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = os.path.join(output_dir, f"model_size_heatmap_{timestamp}.png")
    plt.savefig(fig_path, dpi=dpi)
    print(f"Model-Size heatmap saved to {fig_path}")
    
    return fig_path

def generate_detailed_heatmaps(results, output_dir, figsize, dpi, title):
    """Generate detailed heatmaps for each font size, showing performance across models and fonts."""
    all_sizes = set()
    all_fonts = set()
    model_names = [model_name for model_name, _ in results]
    
    # Collect all sizes and fonts
    for _, result in results:
        # For sizes
        all_sizes.update(result["accuracy_by_font_size"].keys())
        
        # For fonts
        all_fonts.update(result["accuracy_by_font"].keys())
    
    # Convert sizes to integers and sort
    font_sizes = sorted([int(size) for size in all_sizes])
    fonts = sorted(all_fonts)
    
    heatmap_paths = []
    
    # Generate a detailed heatmap for each font size
    for size in font_sizes:
        size_str = str(size)
        
        # Create data matrix for this font size
        data = np.zeros((len(model_names), len(fonts)))
        
        # Fill data matrix with character accuracy values
        for i, (_, result) in enumerate(results):
            if "accuracy_by_font_size_and_font" in result and size_str in result["accuracy_by_font_size_and_font"]:
                for j, font in enumerate(fonts):
                    if font in result["accuracy_by_font_size_and_font"][size_str]:
                        data[i, j] = result["accuracy_by_font_size_and_font"][size_str][font]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate heatmap
        sns.heatmap(data, annot=True, fmt=".2%", cmap="YlGnBu", vmin=0, vmax=1,
                    xticklabels=fonts, yticklabels=model_names, 
                    cbar_kws={'label': 'Character Accuracy'})
        
        # Configure plot
        plt.title(f"{title}: {size}pt Font Size Across Models and Fonts")
        plt.tight_layout()
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fig_path = os.path.join(output_dir, f"detailed_heatmap_{size}pt_{timestamp}.png")
        plt.savefig(fig_path, dpi=dpi)
        print(f"Detailed heatmap for {size}pt saved to {fig_path}")
        
        heatmap_paths.append(fig_path)
    
    return heatmap_paths

def generate_font_heatmaps(results, output_dir, figsize, dpi, title):
    """Generate detailed heatmaps for each font, showing performance across models and font sizes."""
    all_sizes = set()
    all_fonts = set()
    model_names = [model_name for model_name, _ in results]
    
    # Collect all sizes and fonts
    for _, result in results:
        # For sizes
        all_sizes.update(result["accuracy_by_font_size"].keys())
        
        # For fonts
        all_fonts.update(result["accuracy_by_font"].keys())
    
    # Convert sizes to integers and sort
    font_sizes = sorted([int(size) for size in all_sizes])
    fonts = sorted(all_fonts)
    
    heatmap_paths = []
    
    # Generate a detailed heatmap for each font
    for font in fonts:
        # Create data matrix for this font
        data = np.zeros((len(model_names), len(font_sizes)))
        
        # Fill data matrix with character accuracy values
        for i, (_, result) in enumerate(results):
            if "accuracy_by_font_size_and_font" in result:
                for j, size in enumerate(font_sizes):
                    size_str = str(size)
                    if size_str in result["accuracy_by_font_size_and_font"] and font in result["accuracy_by_font_size_and_font"][size_str]:
                        data[i, j] = result["accuracy_by_font_size_and_font"][size_str][font]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate heatmap
        sns.heatmap(data, annot=True, fmt=".2%", cmap="YlGnBu", vmin=0, vmax=1,
                    xticklabels=[f"{size}pt" for size in font_sizes], yticklabels=model_names, 
                    cbar_kws={'label': 'Character Accuracy'})
        
        # Configure plot
        plt.title(f"{title}: {font} Font Across Models and Sizes")
        plt.tight_layout()
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fig_path = os.path.join(output_dir, f"font_heatmap_{font}_{timestamp}.png")
        plt.savefig(fig_path, dpi=dpi)
        print(f"Font heatmap for {font} saved to {fig_path}")
        
        heatmap_paths.append(fig_path)
    
    return heatmap_paths

def main():
    args = parse_args()
    
    # Parse figsize
    try:
        figsize = tuple(map(float, args.figsize.split(',')))
        if len(figsize) != 2:
            raise ValueError()
    except:
        print(f"Invalid figsize: {args.figsize}, using default (14,12)")
        figsize = (14, 12)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load results
    results = load_results(args.results_dir)
    print(f"Loaded results for {len(results)} models")
    
    # Generate all heatmaps
    basic_heatmap = generate_basic_heatmap(results, args.output_dir, figsize, args.dpi, args.title)
    size_heatmap = generate_font_size_heatmap(results, args.output_dir, figsize, args.dpi, args.title)
    detailed_heatmaps = generate_detailed_heatmaps(results, args.output_dir, figsize, args.dpi, args.title)
    font_heatmaps = generate_font_heatmaps(results, args.output_dir, figsize, args.dpi, args.title)
    
    print(f"\nAll heatmap visualizations created:")
    print(f"  Basic model-font heatmap: {basic_heatmap}")
    print(f"  Model-size heatmap: {size_heatmap}")
    print(f"  Detailed size-specific heatmaps: {len(detailed_heatmaps)} heatmaps")
    print(f"  Font-specific heatmaps: {len(font_heatmaps)} heatmaps")

if __name__ == "__main__":
    main()