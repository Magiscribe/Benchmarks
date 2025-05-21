@echo off
echo Running AI Spy Visualizer...
echo.

:: Activate virtual environment and run the visualizer
call venv\Scripts\activate && python visualizations.py --data-dir data

echo.
if %ERRORLEVEL% EQU 0 (
    echo Visualization completed successfully!
) else (
    echo Error: Visualization failed. 
    echo Make sure matplotlib is installed: pip install matplotlib
)

:: Keep the window open
pause