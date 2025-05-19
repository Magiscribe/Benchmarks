#!/bin/bash
# Report generator script for AI Spy benchmark

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Make sure you've installed dependencies."
    echo "Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check for ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ANTHROPIC_API_KEY environment variable not set."
    echo "Please set your API key using: export ANTHROPIC_API_KEY=your_api_key"
    exit 1
fi

# Check if LaTeX is available
if command -v pdflatex >/dev/null 2>&1; then
    echo "LaTeX (pdflatex) found. Using LaTeX for PDF generation."
    python generate_report.py --data-dir data --output-path AI_Spy_Report.pdf
else
    echo "LaTeX (pdflatex) not found. Using ReportLab for PDF generation."
    python generate_report.py --data-dir data --output-path AI_Spy_Report.pdf --use-reportlab
fi

# Print success message
if [ $? -eq 0 ]; then
    echo ""
    echo "Report generated successfully. Check AI_Spy_Report.pdf"
    echo ""
else
    echo ""
    echo "Error generating report. Check error messages above."
    echo ""
fi