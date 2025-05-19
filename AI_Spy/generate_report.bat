@echo off
REM Report generator batch file for AI Spy benchmark

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Make sure you've installed dependencies.
    echo Run: python -m venv venv ^& venv\Scripts\activate.bat ^& pip install -r requirements.txt
    exit /b 1
)

REM Check for ANTHROPIC_API_KEY
if "%ANTHROPIC_API_KEY%"=="" (
    echo ANTHROPIC_API_KEY environment variable not set.
    echo Please set your API key using: set ANTHROPIC_API_KEY=your_api_key
    exit /b 1
)

REM Check if LaTeX is available
where pdflatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo LaTeX (pdflatex) not found. Using ReportLab for PDF generation.
    python generate_report.py --data-dir data --output-path AI_Spy_Report.pdf --use-reportlab
) else (
    echo LaTeX (pdflatex) found. Using LaTeX for PDF generation.
    python generate_report.py --data-dir data --output-path AI_Spy_Report.pdf
)

REM Print success message
if %ERRORLEVEL% equ 0 (
    echo.
    echo Report generated successfully. Check AI_Spy_Report.pdf
    echo.
) else (
    echo.
    echo Error generating report. Check error messages above.
    echo.
)

REM Keep terminal open
pause