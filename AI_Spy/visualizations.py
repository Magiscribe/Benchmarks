#!/usr/bin/env python3
"""
Visualization generator for AI Spy benchmark results.
"""

import os
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Generate visualizations for AI Spy benchmark results")
    
    # Support either individual result files or a directory containing results
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--results", nargs="+",
                       help="Paths to result JSON files")
    group.add_argument("--results-dir", type=str,
                       help="Directory containing result JSON files (must end with _results.json)")
    group.add_argument("--data-dir", type=str,
                       help="Path to data directory (will use data-dir/results for results and data-dir/visualizations for output)")
    
    parser.add_argument("--output-dir", type=str, default=None,
                       help="Directory to save visualizations (default: visualizations or data-dir/visualizations if --data-dir is used)")
    parser.add_argument("--dpi", type=int, default=300,
                       help="DPI for saved figures (default: 300)")
    parser.add_argument("--figsize", type=str, default="12,8",
                       help="Figure size in inches as width,height (default: 12,8)")
    parser.add_argument("--title", type=str, default="AI Spy Benchmark Results",
                       help="Main title for visualizations")
    parser.add_argument("--min-models", type=int, default=2,
                       help="Minimum number of model results required (default: 2)")
    
    return parser.parse_args()

def load_results(result_files):
    """Load results from JSON files."""
    results = []
    for file_path in result_files:
        if not os.path.exists(file_path):
            print(f"Warning: Result file {file_path} not found, skipping")
            continue
            
        # Extract model name from filename
        model_name = os.path.basename(file_path).replace("_results.json", "")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                results.append((model_name, data))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if not results:
        raise ValueError("No valid result files found")
    
    return results

def generate_font_accuracy_chart(results, output_dir, figsize, dpi, title):
    """Generate bar chart comparing model accuracy across different fonts."""
    # Extract font accuracy data
    font_data = {}
    model_names = []
    
    for model_name, result in results:
        model_names.append(model_name)
        for font, accuracy in result["accuracy_by_font"].items():
            if font not in font_data:
                font_data[font] = []
            font_data[font].append(accuracy)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Bar chart parameters
    fonts = list(font_data.keys())
    num_models = len(model_names)
    bar_width = 0.8 / num_models
    
    # Generate positions for grouped bars
    positions = np.arange(len(fonts))
    
    # Plot bars for each model
    for i, model_name in enumerate(model_names):
        model_positions = positions + (i - num_models/2 + 0.5) * bar_width
        accuracies = [font_data[font][i] for font in fonts]
        ax.bar(model_positions, accuracies, width=bar_width, label=model_name)
    
    # Configure plot
    ax.set_title(f"{title}: Accuracy by Font")
    ax.set_xlabel("Font")
    ax.set_ylabel("Character Accuracy")
    ax.set_xticks(positions)
    ax.set_xticklabels(fonts)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend()
    ax.set_ylim(0, 1.05)  # 0-100% with a little headroom
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add percentage values on top of bars
    for i, model_name in enumerate(model_names):
        model_positions = positions + (i - num_models/2 + 0.5) * bar_width
        accuracies = [font_data[font][i] for font in fonts]
        
        for x, y in zip(model_positions, accuracies):
            ax.text(x, y + 0.01, f"{y:.1%}", ha='center', va='bottom', fontsize=8)
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = os.path.join(output_dir, f"font_accuracy_{timestamp}.png")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=dpi)
    print(f"Font accuracy chart saved to {fig_path}")
    
    return fig_path

def generate_fontsize_accuracy_chart(results, output_dir, figsize, dpi, title):
    """Generate scatter plot of accuracy vs font size for each model."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color cycle for different models
    colors = plt.cm.tab10.colors
    
    # Plot accuracy vs font size for each model
    for i, (model_name, result) in enumerate(results):
        # Extract data points
        sizes = []
        accuracies = []
        
        # Sort sizes to connect points in order
        for size, accuracy in sorted(result["accuracy_by_font_size"].items(), key=lambda x: int(x[0])):
            sizes.append(int(size))
            accuracies.append(accuracy)
        
        # Plot points and line
        color = colors[i % len(colors)]
        ax.scatter(sizes, accuracies, label=model_name, color=color, s=50, zorder=3)
        ax.plot(sizes, accuracies, color=color, alpha=0.7, zorder=2)
        
        # Add accuracy values as text
        for size, acc in zip(sizes, accuracies):
            ax.text(size, acc + 0.01, f"{acc:.1%}", ha='center', va='bottom', fontsize=8, color=color)
    
    # Configure plot
    ax.set_title(f"{title}: Accuracy by Font Size")
    ax.set_xlabel("Font Size (pt)")
    ax.set_ylabel("Character Accuracy")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend()
    ax.set_ylim(0, 1.05)  # 0-100% with a little headroom
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Custom x-axis with more appropriate ticks
    all_sizes = []
    for _, result in results:
        all_sizes.extend([int(size) for size in result["accuracy_by_font_size"].keys()])
    
    if all_sizes:
        min_size = max(1, min(all_sizes))
        max_size = max(all_sizes)
        
        # Set reasonable ticks based on range
        if max_size - min_size > 50:
            tick_step = 10
        elif max_size - min_size > 20:
            tick_step = 5
        else:
            tick_step = 2
            
        ticks = list(range(min_size, max_size + tick_step, tick_step))
        ax.set_xticks(ticks)
        
        # Set x-axis limits with a bit of padding
        ax.set_xlim(min_size - tick_step/2, max_size + tick_step/2)
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = os.path.join(output_dir, f"fontsize_accuracy_{timestamp}.png")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=dpi)
    print(f"Font size accuracy chart saved to {fig_path}")
    
    return fig_path

def main():
    args = parse_args()
    
    # Handle directory setup based on arguments
    if args.data_dir:
        # If data-dir is provided, use its subdirectories
        results_dir = os.path.join(args.data_dir, "results")
        if args.output_dir is None:
            args.output_dir = os.path.join(args.data_dir, "visualizations")
        
        # Find result files in the results directory
        import glob
        result_files = glob.glob(os.path.join(results_dir, "*_results.json"))
        if not result_files:
            print(f"No result files found in {results_dir}")
            return
        print(f"Looking for result files in: {results_dir}")
        print(f"Found {len(result_files)} result files: {[os.path.basename(f) for f in result_files]}")
    elif args.results_dir:
        # If results-dir is provided directly
        import glob
        result_files = glob.glob(os.path.join(args.results_dir, "*_results.json"))
        if not result_files:
            print(f"No result files found in {args.results_dir}")
            return
        print(f"Found {len(result_files)} result files in {args.results_dir}")
    else:
        # Otherwise, use the explicitly provided result files
        result_files = args.results
    
    # Use default output directory if not specified
    if args.output_dir is None:
        args.output_dir = "visualizations"
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Parse figsize
    try:
        figsize = tuple(map(float, args.figsize.split(',')))
        if len(figsize) != 2:
            raise ValueError()
    except:
        print(f"Invalid figsize: {args.figsize}, using default (12,8)")
        figsize = (12, 8)
    
    # Check if we have enough models
    if len(result_files) < args.min_models:
        print(f"Not enough model results found. Need at least {args.min_models}, found {len(result_files)}")
        return
    
    print(f"Generating visualizations for {len(result_files)} model results...")
    
    # Load results
    results = load_results(result_files)
    
    # Generate visualizations
    font_chart_path = generate_font_accuracy_chart(results, args.output_dir, figsize, args.dpi, args.title)
    fontsize_chart_path = generate_fontsize_accuracy_chart(results, args.output_dir, figsize, args.dpi, args.title)
    
    print(f"\nVisualizations generated:")
    print(f"  Font accuracy: {font_chart_path}")
    print(f"  Font size accuracy: {fontsize_chart_path}")

if __name__ == "__main__":
    main()