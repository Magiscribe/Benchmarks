# AI Spy Report Generator

The report generator module creates academic-style PDF reports from AI Spy benchmark results.

## Features

- Analyzes all benchmark results and visualizations
- Uses the Anthropic Claude API to generate academic-style paper content
- Compiles the report into a professional PDF using LaTeX or ReportLab
- Includes tables, charts, and analysis of model performance
- Structured like an academic paper with abstract, methodology, results, and discussion

## Prerequisites

- Python 3.8+ with AI Spy dependencies installed
- Anthropic API key (Claude model access)
- For LaTeX compilation (recommended):
  - For Ubuntu/Debian: `sudo apt-get install texlive-full`
  - For macOS: Install MacTeX from https://tug.org/mactex/
  - For Windows: Install MiKTeX from https://miktex.org/
- Alternatively, ReportLab can be used for PDF generation if LaTeX is not available:
  - Install with: `pip install reportlab`

## Usage

### Basic Usage

Windows:
```
generate_report.bat
```

Linux/macOS:
```bash
./generate_report.sh
```

### Advanced Options

```bash
python generate_report.py --data-dir data --output-path AI_Spy_Report.pdf --model claude-3-7-sonnet-20250219 --title "Custom Report Title" --authors "Your Name" --skip-latex
```

### Command-line Options

- `--api-key KEY`: Anthropic API key (default: uses ANTHROPIC_API_KEY environment variable)
- `--model MODEL`: Claude model to use (default: claude-3-7-sonnet-20250219)
- `--data-dir DIR`: Path to data directory containing 'results' and 'visualizations' folders
- `--output-path PATH`: Output path for the PDF report
- `--title TEXT`: Title for the report
- `--authors TEXT`: Authors for the report
- `--affiliation TEXT`: Affiliation for the report
- `--email EMAIL`: Contact email for the report
- `--skip-latex`: Skip LaTeX compilation (outputs .tex file only)
- `--use-reportlab`: Use ReportLab for PDF generation instead of LaTeX (simpler but less polished)

## Report Structure

The generated report follows a standard academic paper structure:

1. **Title Page** - Title, authors, affiliation, date
2. **Abstract** - Summary of the benchmark and key findings
3. **Introduction** - Background on visual acuity in AI models
4. **Related Work** - Comparison to other vision model benchmarks
5. **Methodology** - Detailed explanation of the AI Spy benchmark design
6. **Experimental Setup** - Description of the tested models and configuration
7. **Results** - Analysis of model performance with visualizations
8. **Discussion** - Interpretation of results and key insights
9. **Conclusion** - Summary of findings and implications
10. **References** - Academic citations

## PDF Generation Options

The script offers two methods for generating the final PDF:

1. **LaTeX (Default)** - Produces a professional, academic-style document with proper typesetting
   - Requires LaTeX installation
   - Better handling of mathematical notation, references, and typography
   - May require troubleshooting LaTeX-related issues on some systems

2. **ReportLab (Fallback)** - Simpler PDF generation built into Python
   - Doesn't require external software installation beyond Python packages
   - Simpler layout but more reliable on systems without LaTeX
   - Automatically used if LaTeX fails, or can be explicitly selected with `--use-reportlab`

## Output Files

The script generates the following files:
- `AI_Spy_Report.tex` - LaTeX source file
- `AI_Spy_Report.pdf` - Compiled PDF report (if LaTeX is installed or ReportLab is used)
- `report_assets/` - Directory containing report images and resources

## Example Command

```bash
# Set your API key
export ANTHROPIC_API_KEY=your_api_key_here

# Generate a full report with all available data using ReportLab
python generate_report.py --data-dir data --title "AI Visual Acuity: Benchmarking Vision Models" --authors "Research Team" --affiliation "AI Lab" --model claude-3-7-sonnet-20250219 --use-reportlab
```