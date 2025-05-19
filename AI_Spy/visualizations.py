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
    font_sizes_data = {}
    
    for model_name, result in results:
        model_names.append(model_name)
        for font, accuracy in result["accuracy_by_font"].items():
            if font not in font_data:
                font_data[font] = []
            font_data[font].append(accuracy)
        
        # Also collect font size data for per-size charts
        for size, accuracy in result["accuracy_by_font_size"].items():
            if size not in font_sizes_data:
                font_sizes_data[size] = []
            font_sizes_data[size].append(accuracy)
    
    # Create main figure for all fonts
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
    
    # Removed percentage values on top of bars as requested
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = os.path.join(output_dir, f"font_type_accuracy_{timestamp}.png")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=dpi)
    print(f"Font accuracy chart saved to {fig_path}")
    
    # Create separate charts for each font size
    chart_paths = [fig_path]
    
    # Check if we have font accuracy data per size per font in any result
    has_detailed_data = False
    for _, result in results:
        if result.get("accuracy_by_font_size_and_font"):
            has_detailed_data = True
            break
    
    # If no detailed data is available, let's analyze image_results to extract it
    font_size_font_data = {}
    if not has_detailed_data:
        # First, collect results by font and size
        for _, result in results:
            if "image_results" in result:
                for img_result in result["image_results"]:
                    if "metadata" in img_result and "font" in img_result["metadata"]:
                        font = img_result["metadata"]["font"]
                        # Check if row_data is available
                        if "row_data" in img_result["metadata"]:
                            for row_data in img_result["metadata"]["row_data"]:
                                if "row" in row_data and "size" in row_data and "char_accuracy" in row_data:
                                    size = str(row_data["size"])
                                    accuracy = row_data.get("char_accuracy", 0)
                                    
                                    # Store in our structure
                                    if size not in font_size_font_data:
                                        font_size_font_data[size] = {}
                                    
                                    if font not in font_size_font_data[size]:
                                        font_size_font_data[size][font] = []
                                    
                                    font_size_font_data[size][font].append(accuracy)
    
    # Create a chart for each font size
    for size in sorted(font_sizes_data.keys(), key=int):
        # Create a new figure for this font size
        fig_size, ax_size = plt.subplots(figsize=figsize)
        
        # Bar chart parameters
        fonts = list(font_data.keys())
        num_models = len(model_names)
        bar_width = 0.8 / num_models
        
        # Generate positions for grouped bars
        positions = np.arange(len(fonts))
        
        # Create a data structure to hold the font-specific accuracies for each model
        model_font_accuracies = {}
        
        # If we have the detailed data directly from results
        has_size_data = False
        for model_idx, (model_name, result) in enumerate(results):
            if result.get("accuracy_by_font_size_and_font") and size in result.get("accuracy_by_font_size_and_font", {}):
                has_size_data = True
                model_font_accuracies[model_name] = []
                for font in fonts:
                    if font in result["accuracy_by_font_size_and_font"][size]:
                        model_font_accuracies[model_name].append(result["accuracy_by_font_size_and_font"][size][font])
                    else:
                        # If no data for this font at this size, use 0 
                        model_font_accuracies[model_name].append(0)
        
        # If we don't have detailed data in the results, use our extracted data
        if not has_size_data and size in font_size_font_data:
            for model_idx, (model_name, _) in enumerate(results):
                model_font_accuracies[model_name] = []
                for font in fonts:
                    if font in font_size_font_data[size]:
                        # Use the average accuracy for this font and size
                        font_accs = font_size_font_data[size][font]
                        if font_accs:
                            model_font_accuracies[model_name].append(sum(font_accs) / len(font_accs))
                        else:
                            model_font_accuracies[model_name].append(0)
                    else:
                        model_font_accuracies[model_name].append(0)
        
        # If we still don't have detailed data, use the average for each font
        if not model_font_accuracies:
            # Get the size accuracy for each model
            model_size_accuracies = {}
            for model_name, result in results:
                if size in result.get("accuracy_by_font_size", {}):
                    model_size_accuracies[model_name] = result["accuracy_by_font_size"][size]
                else:
                    model_size_accuracies[model_name] = 0
            
            # Apply that accuracy to each font for the model
            for model_name in model_names:
                if model_name in model_size_accuracies:
                    model_font_accuracies[model_name] = [model_size_accuracies[model_name]] * len(fonts)
                else:
                    model_font_accuracies[model_name] = [0] * len(fonts)
        
        # Plot the data
        for i, model_name in enumerate(model_names):
            if model_name in model_font_accuracies:
                model_positions = positions + (i - num_models/2 + 0.5) * bar_width
                ax_size.bar(model_positions, model_font_accuracies[model_name], width=bar_width, label=model_name)
        
        # Configure plot
        ax_size.set_title(f"{title}: Accuracy by Font (Font Size {size}pt)")
        ax_size.set_xlabel("Font")
        ax_size.set_ylabel("Character Accuracy")
        ax_size.set_xticks(positions)
        ax_size.set_xticklabels(fonts)
        ax_size.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax_size.legend()
        ax_size.set_ylim(0, 1.05)  # 0-100% with a little headroom
        ax_size.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        size_fig_path = os.path.join(output_dir, f"font_type_accuracy_size_{size}pt_{timestamp}.png")
        fig_size.tight_layout()
        fig_size.savefig(size_fig_path, dpi=dpi)
        print(f"Font accuracy chart for size {size}pt saved to {size_fig_path}")
        chart_paths.append(size_fig_path)
    
    return chart_paths

def generate_font_size_accuracy_chart(results, output_dir, figsize, dpi, title):
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
        
        # Removed text annotations as requested
    
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
    fig_path = os.path.join(output_dir, f"font_size_accuracy_{timestamp}.png")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=dpi)
    print(f"Font size accuracy chart saved to {fig_path}")
    
    return fig_path

def generate_summary_tables(results, output_dir):
    """Generate summary tables in CSV format."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Overall model performance table
    overall_table_path = os.path.join(output_dir, f"overall_accuracy_{timestamp}.csv")
    with open(overall_table_path, 'w') as f:
        # Headers
        f.write("Model,Character Accuracy,Row Accuracy\n")
        
        # Sort by character accuracy
        sorted_results = sorted(results, key=lambda x: x[1]["overall_char_accuracy"], reverse=True)
        
        # Data rows
        for model_name, result in sorted_results:
            f.write(f"{model_name},{result['overall_char_accuracy']:.4f},{result['overall_row_accuracy']:.4f}\n")
    
    # 2. Font accuracy table
    font_table_path = os.path.join(output_dir, f"font_accuracy_{timestamp}.csv")
    with open(font_table_path, 'w') as f:
        # Get all fonts
        all_fonts = set()
        for _, result in results:
            all_fonts.update(result["accuracy_by_font"].keys())
        
        # Headers
        f.write("Model," + ",".join(sorted(all_fonts)) + "\n")
        
        # Data rows
        for model_name, result in sorted_results:
            f.write(f"{model_name}")
            for font in sorted(all_fonts):
                accuracy = result["accuracy_by_font"].get(font, 0)
                f.write(f",{accuracy:.4f}")
            f.write("\n")
    
    # 3. Font size accuracy table
    size_table_path = os.path.join(output_dir, f"font_size_accuracy_{timestamp}.csv")
    with open(size_table_path, 'w') as f:
        # Get all font sizes
        all_sizes = set()
        for _, result in results:
            all_sizes.update(result["accuracy_by_font_size"].keys())
        
        # Convert to integers and sort
        all_sizes = sorted([int(size) for size in all_sizes])
        
        # Headers
        f.write("Model," + ",".join([f"{size}pt" for size in all_sizes]) + "\n")
        
        # Data rows
        for model_name, result in sorted_results:
            f.write(f"{model_name}")
            for size in all_sizes:
                size_str = str(size)
                accuracy = result["accuracy_by_font_size"].get(size_str, 0)
                f.write(f",{accuracy:.4f}")
            f.write("\n")
    
    # 4. Create a separate table for each font size showing font-specific performance
    font_size_specific_tables = {}
    
    # Get all fonts
    all_fonts = set()
    for _, result in results:
        all_fonts.update(result["accuracy_by_font"].keys())
    
    # Get all font sizes
    all_sizes = set()
    for _, result in results:
        all_sizes.update(result["accuracy_by_font_size"].keys())
    
    # Convert to integers and sort
    all_sizes = sorted([int(size) for size in all_sizes])
    
    for size in all_sizes:
        size_str = str(size)
        size_font_table_path = os.path.join(output_dir, f"size_{size}pt_by_font_accuracy_{timestamp}.csv")
        
        with open(size_font_table_path, 'w') as f:
            # Headers
            f.write(f"Model," + ",".join(sorted(all_fonts)) + "\n")
            
            # Data rows
            for model_name, result in sorted_results:
                f.write(f"{model_name}")
                
                # Check if we have detailed size+font data
                if "accuracy_by_font_size_and_font" in result and size_str in result["accuracy_by_font_size_and_font"]:
                    # Use detailed data
                    size_font_data = result["accuracy_by_font_size_and_font"][size_str]
                    for font in sorted(all_fonts):
                        accuracy = size_font_data.get(font, 0)
                        f.write(f",{accuracy:.4f}")
                else:
                    # Use general font accuracy as fallback
                    for font in sorted(all_fonts):
                        accuracy = result["accuracy_by_font"].get(font, 0)
                        f.write(f",{accuracy:.4f}")
                
                f.write("\n")
                
        font_size_specific_tables[size] = size_font_table_path
    
    return {
        "overall": overall_table_path,
        "font": font_table_path,
        "font_size": size_table_path,
        "font_size_specific": font_size_specific_tables
    }

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
    
    # Create tables directory
    tables_dir = os.path.join(args.output_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    
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
    
    # Generate summary tables
    print("Generating summary tables...")
    table_paths = generate_summary_tables(results, tables_dir)
    
    # Generate visualizations
    print("Generating charts...")
    font_chart_paths = generate_font_accuracy_chart(results, args.output_dir, figsize, args.dpi, args.title)
    font_size_chart_path = generate_font_size_accuracy_chart(results, args.output_dir, figsize, args.dpi, args.title)
    
    print(f"\nVisualizations generated:")
    print(f"  Main font accuracy: {font_chart_paths[0]}")
    print(f"  Font size-specific charts: {len(font_chart_paths)-1} charts")
    for i, path in enumerate(font_chart_paths[1:], 1):
        print(f"    - Chart {i}: {path}")
    print(f"  Font size accuracy: {font_size_chart_path}")
    
    print(f"\nSummary tables generated:")
    print(f"  Overall model performance: {table_paths['overall']}")
    print(f"  Font accuracy by model: {table_paths['font']}")
    print(f"  Font size accuracy by model: {table_paths['font_size']}")
    print(f"  Font-size specific tables:")
    for size, path in sorted(table_paths['font_size_specific'].items()):
        print(f"    - Size {size}pt: {path}")

if __name__ == "__main__":
    main()