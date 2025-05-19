#!/usr/bin/env python3
"""
Report generator for AI Spy benchmark results.
Creates an academic-style PDF report using Claude API and LaTeX.
"""

import os
import json
import argparse
import glob
import base64
import pandas as pd
import subprocess
import sys
import re
import matplotlib.pyplot as plt
import anthropic
from datetime import datetime
from pathlib import Path

# For reportlab-based PDF generation (fallback if LaTeX is not available)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def parse_args():
    parser = argparse.ArgumentParser(description="Generate academic PDF report for AI Spy benchmark")
    
    parser.add_argument("--api-key", type=str, default=None,
                        help="Anthropic API key (default: uses ANTHROPIC_API_KEY env variable)")
    parser.add_argument("--model", type=str, default="claude-3-7-sonnet-20250219",
                        help="Claude model to use (default: claude-3-7-sonnet-20250219)")
    parser.add_argument("--data-dir", type=str, default="data",
                        help="Path to data directory containing 'results' and 'visualizations' folders")
    parser.add_argument("--output-path", type=str, default="AI_Spy_Report.pdf",
                        help="Output path for the PDF report")
    parser.add_argument("--title", type=str, default="AI Visual Acuity: A Benchmark for Vision Models",
                        help="Title for the report")
    parser.add_argument("--authors", type=str, default="Claude Benchmarking Team",
                        help="Authors for the report")
    parser.add_argument("--affiliation", type=str, default="Anthropic",
                        help="Affiliation for the report")
    parser.add_argument("--email", type=str, default="example@example.com",
                        help="Contact email for the report")
    parser.add_argument("--skip-latex", action="store_true",
                        help="Skip LaTeX compilation (outputs .tex file only)")
    parser.add_argument("--use-reportlab", action="store_true",
                        help="Use ReportLab for PDF generation instead of LaTeX")
    
    return parser.parse_args()

def load_results(results_dir):
    """Load all results from JSON files."""
    results = []
    # Use Path for proper cross-platform path handling
    results_path = Path(results_dir)
    result_files = list(results_path.glob("*_results.json"))
    
    for file_path in sorted(result_files, key=lambda x: x.name):
        model_name = file_path.stem.replace("_results", "")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                results.append((model_name, data))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if not results:
        raise ValueError(f"No valid result files found in {results_dir}")
    
    return results

def load_visualizations(vis_dir):
    """Load all visualization file paths."""
    vis_files = {}
    
    # Use Path for proper cross-platform path handling
    vis_path = Path(vis_dir)
    tables_path = vis_path / "tables"
    
    # Main visualization files
    font_accuracy_files = sorted(list(vis_path.glob("font_type_accuracy_*.png")))
    if font_accuracy_files:
        vis_files["font_accuracy"] = str(font_accuracy_files[-1])
    
    font_size_accuracy_files = sorted(list(vis_path.glob("font_size_accuracy_*.png")))
    if font_size_accuracy_files:
        vis_files["font_size_accuracy"] = str(font_size_accuracy_files[-1])
    
    # Size-specific charts
    vis_files["size_specific"] = {}
    for size_file in sorted(list(vis_path.glob("font_type_accuracy_size_*pt_*.png"))):
        size_match = re.search(r'size_(\d+)pt_', size_file.name)
        if size_match:
            size = size_match.group(1)
            vis_files["size_specific"][size] = str(size_file)
    
    # CSV tables
    vis_files["tables"] = {}
    
    if tables_path.exists():
        # Overall table
        overall_files = sorted(list(tables_path.glob("overall_accuracy_*.csv")))
        if overall_files:
            vis_files["tables"]["overall"] = str(overall_files[-1])
        
        # Font accuracy table
        font_files = sorted(list(tables_path.glob("font_accuracy_*.csv")))
        if font_files:
            vis_files["tables"]["font"] = str(font_files[-1])
        
        # Font size accuracy table
        size_files = sorted(list(tables_path.glob("font_size_accuracy_*.csv")))
        if size_files:
            vis_files["tables"]["font_size"] = str(size_files[-1])
        
        # Size-specific font tables
        vis_files["tables"]["size_specific"] = {}
        for size_file in sorted(list(tables_path.glob("size_*pt_by_font_accuracy_*.csv"))):
            size_match = re.search(r'size_(\d+)pt_', size_file.name)
            if size_match:
                size = size_match.group(1)
                vis_files["tables"]["size_specific"][size] = str(size_file)
    
    return vis_files

def load_csv_data(csv_path):
    """Load and format CSV data."""
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error loading CSV {csv_path}: {e}")
        return None

def image_to_base64(image_path):
    """Convert image to base64 encoding."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_report_data(results, vis_files):
    """Create structured data for the report."""
    report_data = {
        "results": results,
        "visualizations": {},
        "tables": {}
    }
    
    # Add main visualizations as base64
    if "font_accuracy" in vis_files and os.path.exists(vis_files["font_accuracy"]):
        report_data["visualizations"]["font_accuracy"] = {
            "path": vis_files["font_accuracy"],
            "base64": image_to_base64(vis_files["font_accuracy"])
        }
    
    if "font_size_accuracy" in vis_files and os.path.exists(vis_files["font_size_accuracy"]):
        report_data["visualizations"]["font_size_accuracy"] = {
            "path": vis_files["font_size_accuracy"],
            "base64": image_to_base64(vis_files["font_size_accuracy"])
        }
    
    # Add size-specific visualizations (selected ones)
    if "size_specific" in vis_files:
        report_data["visualizations"]["size_specific"] = {}
        # Only include a few representative sizes to avoid overloading
        for size in ["24", "16", "12", "9"]:
            if size in vis_files["size_specific"] and os.path.exists(vis_files["size_specific"][size]):
                report_data["visualizations"]["size_specific"][size] = {
                    "path": vis_files["size_specific"][size],
                    "base64": image_to_base64(vis_files["size_specific"][size])
                }
    
    # Add tables data
    if "tables" in vis_files:
        if "overall" in vis_files["tables"] and os.path.exists(vis_files["tables"]["overall"]):
            report_data["tables"]["overall"] = load_csv_data(vis_files["tables"]["overall"])
        
        if "font" in vis_files["tables"] and os.path.exists(vis_files["tables"]["font"]):
            report_data["tables"]["font"] = load_csv_data(vis_files["tables"]["font"])
        
        if "font_size" in vis_files["tables"] and os.path.exists(vis_files["tables"]["font_size"]):
            report_data["tables"]["font_size"] = load_csv_data(vis_files["tables"]["font_size"])
    
    # Add metadata
    report_data["metadata"] = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "num_models": len(results),
        "model_names": [model_name for model_name, _ in results],
        "font_sizes": sorted([int(size) for size in results[0][1]["accuracy_by_font_size"].keys()]),
        "fonts": sorted(list(results[0][1]["accuracy_by_font"].keys()))
    }
    
    # Calculate averages and rankings
    if "tables" in report_data and "overall" in report_data["tables"]:
        overall_df = report_data["tables"]["overall"]
        if overall_df is not None and not overall_df.empty:
            report_data["best_model"] = overall_df.iloc[0]["Model"]
            report_data["average_accuracy"] = overall_df["Character Accuracy"].mean()
    
    return report_data

def generate_report_with_claude(client, model, report_data, args):
    """Generate academic report text using Claude API."""
    
    # Create prompt with report data
    prompt = f"""You are an academic researcher specialized in machine learning and computer vision. Your task is to write a formal academic paper in the style of an arXiv submission that reports on benchmark results for vision models.

# Report Information
- Title: {args.title}
- Authors: {args.authors}
- Affiliation: {args.affiliation}
- Contact: {args.email}

# Report Structure
This academic paper should include:
1. Abstract - A concise summary of the benchmark, methods, and key findings
2. Introduction - Background on the importance of visual acuity in AI models, explanation of the benchmark approach
3. Related Work - Brief overview of other vision model benchmarks and how this one differs
4. Methodology - Detailed explanation of the AI Spy benchmark design, including eye chart generation, fonts, sizes, and evaluation metrics
5. Experimental Setup - Description of the tested models and benchmark configuration
6. Results - Analysis of model performance across different fonts and font sizes
7. Discussion - Interpretation of results, comparison between models, key insights, and limitations
8. Conclusion - Summary of findings and implications for future vision model development
9. References - Relevant academic citations in proper format (IEEE style)

# Technical Details
Here's the data from our AI Spy benchmark that tests how well vision models can read text in eye chart-style images:

## Benchmark Description
AI Spy generates eye chart-style images with standardized font sizes and evaluates how well vision models can read the text, especially as it gets smaller. The benchmark provides a quantitative way to assess the "visual acuity" of AI vision systems across multiple models.

## Models Tested
{", ".join(report_data["metadata"]["model_names"])}

## Font Sizes Tested (in points)
{", ".join(str(size) for size in report_data["metadata"]["font_sizes"])}

## Fonts Tested
{", ".join(report_data["metadata"]["fonts"])}

## Overall Results Summary
"""

    # Add overall results table if available
    if "tables" in report_data and "overall" in report_data["tables"] and report_data["tables"]["overall"] is not None:
        overall_df = report_data["tables"]["overall"]
        prompt += f"""
Overall Character Accuracy by Model:
{overall_df.to_string(index=False)}

"""

    # Add font results table if available
    if "tables" in report_data and "font" in report_data["tables"] and report_data["tables"]["font"] is not None:
        font_df = report_data["tables"]["font"]
        prompt += f"""
Font-specific Accuracy by Model:
{font_df.to_string(index=False)}

"""

    # Add font size results table if available
    if "tables" in report_data and "font_size" in report_data["tables"] and report_data["tables"]["font_size"] is not None:
        size_df = report_data["tables"]["font_size"]
        prompt += f"""
Font Size Accuracy by Model:
{size_df.to_string(index=False)}

"""

    # Add key observations about model performance
    prompt += """
# Key Observations to Highlight

1. Compare how model accuracy decreases as font size gets smaller
2. Identify which fonts are most challenging/easiest for the models
3. Highlight any significant differences between model families
4. Discuss the "threshold" font size where performance significantly drops
5. Compare the results to human visual acuity where possible
6. Discuss limitations of the benchmark methodology

# Output Format Instructions
- Write in a formal, academic tone appropriate for a conference or journal publication
- Structure the paper with proper academic sections and numbering
- Include LaTeX math notation where appropriate for metrics
- Reference appropriate academic papers in the field of computer vision and machine learning
- Include descriptions of the visualizations that would accompany each section
- Focus on objective analysis with clearly supported conclusions
- For the references section, include relevant citations for vision models, benchmarks, and visual perception research

Generate the full text of this academic paper in LaTeX format, properly formatted for arXiv submission.
"""

    # Call Claude API to generate report
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.2,
            system="You are an expert academic researcher in computer vision and machine learning, specializing in writing formal papers about AI benchmark results.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract LaTeX content
        latex_content = response.content[0].text
        return latex_content
    
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        raise

def prepare_latex_document(latex_content, args, vis_files):
    """Prepare a complete LaTeX document with images."""
    
    # Create directory for report assets
    output_dir = os.path.dirname(os.path.abspath(args.output_path))
    assets_dir = os.path.join(output_dir, "report_assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Copy main visualization files
    image_paths = {}
    
    # Process font accuracy chart
    if "font_accuracy" in vis_files and os.path.exists(vis_files["font_accuracy"]):
        dest_path = os.path.join(assets_dir, "font_accuracy.png")
        try:
            with open(vis_files["font_accuracy"], "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())
            image_paths["font_accuracy"] = "font_accuracy.png"
        except Exception as e:
            print(f"Error copying font accuracy image: {e}")
    
    # Process font size accuracy chart
    if "font_size_accuracy" in vis_files and os.path.exists(vis_files["font_size_accuracy"]):
        dest_path = os.path.join(assets_dir, "font_size_accuracy.png")
        try:
            with open(vis_files["font_size_accuracy"], "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())
            image_paths["font_size_accuracy"] = "font_size_accuracy.png"
        except Exception as e:
            print(f"Error copying font size accuracy image: {e}")
    
    # Process size-specific charts (selected ones)
    if "size_specific" in vis_files:
        image_paths["size_specific"] = {}
        key_sizes = ["24", "16", "12", "9"]  # Representative sizes
        for size in key_sizes:
            if size in vis_files["size_specific"] and os.path.exists(vis_files["size_specific"][size]):
                dest_path = os.path.join(assets_dir, f"size_{size}_pt.png")
                try:
                    with open(vis_files["size_specific"][size], "rb") as src, open(dest_path, "wb") as dst:
                        dst.write(src.read())
                    image_paths["size_specific"][size] = f"size_{size}_pt.png"
                except Exception as e:
                    print(f"Error copying size-specific image for {size}pt: {e}")
    
    # Clean up any LaTeX document structure in the content
    # Remove any existing document class, begin/end document, etc.
    latex_content = re.sub(r'\\documentclass.*?\n', '', latex_content)
    latex_content = re.sub(r'\\begin\{document\}', '', latex_content)
    latex_content = re.sub(r'\\end\{document\}', '', latex_content)
    
    # Create a simple and reliable document structure
    preamble = f"""\\documentclass{{article}}

% Basic packages
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{amsmath}}
\\usepackage{{url}}

% Document information
\\title{{{args.title}}}
\\author{{{args.authors}\\\\{args.affiliation}\\\\{args.email}}}
\\date{{{datetime.now().strftime("%B %d, %Y")}}}

% Image path
\\graphicspath{{{{report_assets/}}}}

\\begin{{document}}
\\maketitle

"""
    
    # Create figure environments for the main visualizations
    figures_section = """
\\section*{Figures}

"""
    
    if "font_accuracy" in image_paths:
        figures_section += """
\\begin{figure}[htbp]
\\centering
\\includegraphics[width=0.9\\textwidth]{font_accuracy.png}
\\caption{Accuracy by font type across different models.}
\\label{fig:font_accuracy}
\\end{figure}

"""
    
    if "font_size_accuracy" in image_paths:
        figures_section += """
\\begin{figure}[htbp]
\\centering
\\includegraphics[width=0.9\\textwidth]{font_size_accuracy.png}
\\caption{Accuracy by font size across different models.}
\\label{fig:font_size_accuracy}
\\end{figure}

"""
    
    # Add selected size-specific figures
    if "size_specific" in image_paths:
        for size, path in image_paths["size_specific"].items():
            figures_section += f"""
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=0.9\\textwidth]{{{path}}}
\\caption{{Performance comparison for {size}pt font size across different fonts.}}
\\label{{fig:size_{size}}}
\\end{{figure}}

"""
    
    # End document
    ending = """
\\end{document}
"""
    
    # Check if there are already figure references in the content
    has_figure_refs = re.search(r'\\includegraphics', latex_content) is not None
    
    # Combine everything
    if has_figure_refs:
        # If Claude already added figure references, use its content
        full_latex = preamble + latex_content + ending
    else:
        # Otherwise add our generated figures section after the content
        full_latex = preamble + latex_content + figures_section + ending
    
    # Create absolute path for output file
    output_tex_path = os.path.join(output_dir, "AI_Spy_Report.tex")
    
    return full_latex, output_tex_path

def compile_latex(tex_path):
    """Compile LaTeX document to PDF."""
    output_dir = os.path.dirname(os.path.abspath(tex_path))
    basename = os.path.splitext(os.path.basename(tex_path))[0]
    pdf_path = os.path.join(output_dir, f"{basename}.pdf")
    
    print(f"Compiling LaTeX document: {tex_path}")
    
    try:
        # Check if pdflatex is available
        process = subprocess.run(
            ["where", "pdflatex"] if sys.platform == "win32" else ["which", "pdflatex"],
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            print("pdflatex command not found. Please install LaTeX.")
            return None
            
        # Run pdflatex twice to resolve references
        # Change directory to output_dir to help with relative paths
        current_dir = os.getcwd()
        os.chdir(output_dir)
        
        for _ in range(2):
            # Use the basename of the tex file since we're already in the directory
            tex_basename = os.path.basename(tex_path)
            process = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_basename],
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                print(f"LaTeX compilation error:")
                output_lines = process.stdout.splitlines()
                # Print relevant error messages
                for i, line in enumerate(output_lines):
                    if "Error" in line or "Fatal" in line:
                        context_start = max(0, i-5)
                        context_end = min(len(output_lines), i+5)
                        print("\n".join(output_lines[context_start:context_end]))
                        break
                
                # Return to original directory
                os.chdir(current_dir)
                return None
        
        # Return to original directory
        os.chdir(current_dir)
        
        if os.path.exists(pdf_path):
            print(f"Successfully compiled PDF: {pdf_path}")
            return pdf_path
        else:
            print(f"PDF file not created despite successful compilation command")
            return None
    
    except Exception as e:
        print(f"Error compiling LaTeX: {e}")
        return None

def generate_simple_pdf(latex_content, args, vis_files, output_path):
    """Generate a simple PDF report using ReportLab as fallback when LaTeX is not available."""
    if not REPORTLAB_AVAILABLE:
        print("ReportLab package is not available. Install it with: pip install reportlab")
        return None
    
    try:
        # Create a PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create custom styles
        styles.add(ParagraphStyle(name='Title', 
                                 parent=styles['Heading1'], 
                                 fontSize=18,
                                 alignment=1,  # Center
                                 spaceAfter=24))
        
        styles.add(ParagraphStyle(name='Author', 
                                 parent=styles['Normal'], 
                                 fontSize=12,
                                 alignment=1,  # Center
                                 spaceAfter=12))
        
        styles.add(ParagraphStyle(name='Heading2', 
                                 parent=styles['Heading2'], 
                                 fontSize=14,
                                 spaceAfter=10,
                                 spaceBefore=20))
        
        # Build the document content
        content = []
        
        # Title
        content.append(Paragraph(args.title, styles['Title']))
        content.append(Paragraph(f"{args.authors}<br/>{args.affiliation}<br/>{args.email}", styles['Author']))
        content.append(Spacer(1, 0.5*inch))
        
        # Convert LaTeX content to plain text sections
        text_content = re.sub(r'\\section\{([^}]+)\}', r'SECTION:\1', latex_content)
        text_content = re.sub(r'\\subsection\{([^}]+)\}', r'SUBSECTION:\1', text_content)
        text_content = re.sub(r'\\begin\{[^}]+\}', '', text_content)
        text_content = re.sub(r'\\end\{[^}]+\}', '', text_content)
        text_content = re.sub(r'\\label\{[^}]+\}', '', text_content)
        text_content = re.sub(r'\\cite\{[^}]+\}', r'[ref]', text_content)
        text_content = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text_content)
        text_content = re.sub(r'\\textit\{([^}]+)\}', r'\1', text_content)
        text_content = re.sub(r'\\includegraphics(\[[^]]*\])?\{[^}]+\}', '[[FIGURE]]', text_content)
        
        # Split into sections
        sections = re.split(r'SECTION:', text_content)
        
        # Process each section
        for section in sections:
            if not section.strip():
                continue
                
            # Extract section title and content
            parts = section.split('\n', 1)
            if len(parts) < 2:
                continue
                
            section_title = parts[0].strip()
            section_content = parts[1].strip()
            
            # Add section heading
            content.append(Paragraph(section_title, styles['Heading2']))
            
            # Add section paragraphs
            paragraphs = re.split(r'\n\n+', section_content)
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                    
                # Check if this is a subsection
                if para.startswith('SUBSECTION:'):
                    subsection_title = para.replace('SUBSECTION:', '').strip()
                    content.append(Paragraph(subsection_title, styles['Heading3']))
                # Regular paragraph
                elif '[[FIGURE]]' not in para:
                    # Replace any LaTeX math with simple text
                    para = re.sub(r'\$([^$]+)\$', r'\1', para)
                    content.append(Paragraph(para, styles['Normal']))
                    content.append(Spacer(1, 0.1*inch))
            
            content.append(Spacer(1, 0.2*inch))
        
        # Add figures
        content.append(Paragraph("Figures", styles['Heading2']))
        
        # Add main visualization images
        if "font_accuracy" in vis_files and os.path.exists(vis_files["font_accuracy"]):
            img = Image(vis_files["font_accuracy"])
            img.drawHeight = 4*inch
            img.drawWidth = 6*inch
            content.append(img)
            content.append(Paragraph("Figure 1: Accuracy by font type across different models.", 
                                    styles['Caption']))
            content.append(Spacer(1, 0.3*inch))
        
        if "font_size_accuracy" in vis_files and os.path.exists(vis_files["font_size_accuracy"]):
            img = Image(vis_files["font_size_accuracy"])
            img.drawHeight = 4*inch
            img.drawWidth = 6*inch
            content.append(img)
            content.append(Paragraph("Figure 2: Accuracy by font size across different models.", 
                                    styles['Caption']))
            content.append(Spacer(1, 0.3*inch))
        
        # Add selected size-specific figures
        if "size_specific" in vis_files:
            key_sizes = ["24", "16", "12", "9"]  # Representative sizes
            fig_num = 3
            for size in key_sizes:
                if size in vis_files["size_specific"] and os.path.exists(vis_files["size_specific"][size]):
                    img = Image(vis_files["size_specific"][size])
                    img.drawHeight = 4*inch
                    img.drawWidth = 6*inch
                    content.append(img)
                    content.append(Paragraph(f"Figure {fig_num}: Performance comparison for {size}pt font size across different fonts.", 
                                            styles['Caption']))
                    content.append(Spacer(1, 0.3*inch))
                    fig_num += 1
        
        # Build the PDF
        doc.build(content)
        print(f"Simple PDF report generated at: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating simple PDF: {e}")
        return None

def main():
    args = parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: No API key provided. Please set the ANTHROPIC_API_KEY environment variable or use --api-key.")
        sys.exit(1)
    
    # Create Claude client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Prepare directories using Path
    data_path = Path(args.data_dir)
    results_dir = data_path / "results"
    vis_dir = data_path / "visualizations"
    
    # Load results and visualizations
    print(f"Loading results from {results_dir}...")
    results = load_results(results_dir)
    
    print(f"Loading visualizations from {vis_dir}...")
    vis_files = load_visualizations(vis_dir)
    
    # Create report data structure
    print("Preparing report data...")
    report_data = create_report_data(results, vis_files)
    
    # Generate report with Claude
    print(f"Generating academic report with Claude {args.model}...")
    latex_content = generate_report_with_claude(client, args.model, report_data, args)
    
    # Prepare complete LaTeX document
    print("Preparing LaTeX document...")
    full_latex, tex_path = prepare_latex_document(latex_content, args, vis_files)
    
    # Write LaTeX file
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(full_latex)
    print(f"LaTeX document written to {tex_path}")
    
    # Skip LaTeX if requested
    if args.skip_latex:
        print(f"\nLaTeX document generated (PDF compilation skipped): {tex_path}")
        return
    
    # Use ReportLab if requested or as fallback
    if args.use_reportlab:
        print("Using ReportLab for PDF generation as requested...")
        pdf_path = generate_simple_pdf(latex_content, args, vis_files, args.output_path)
        if pdf_path:
            print(f"\nReport successfully generated with ReportLab: {pdf_path}")
        else:
            print("\nFailed to generate PDF with ReportLab.")
        return
    
    # Try LaTeX first
    try:
        pdf_path = compile_latex(tex_path)
        if pdf_path:
            print(f"\nReport successfully generated with LaTeX: {pdf_path}")
            return
        else:
            print("\nFailed to compile PDF with LaTeX. Trying ReportLab as fallback...")
    except Exception as e:
        print(f"Error during LaTeX compilation: {e}")
        print("Trying ReportLab as fallback...")
    
    # Use ReportLab as fallback
    if REPORTLAB_AVAILABLE:
        pdf_path = generate_simple_pdf(latex_content, args, vis_files, args.output_path)
        if pdf_path:
            print(f"\nReport successfully generated with ReportLab: {pdf_path}")
        else:
            print("\nFailed to generate PDF with both LaTeX and ReportLab.")
            print(f"LaTeX document is available at: {tex_path}")
    else:
        print("\nReportLab is not available for fallback PDF generation.")
        print("Install it with: pip install reportlab")
        print(f"LaTeX document is available at: {tex_path}")

if __name__ == "__main__":
    main()