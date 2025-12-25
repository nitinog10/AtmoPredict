@echo off
echo Climate Prediction for October 4, 2026
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python from python.org
        pause
        exit /b 1
    ) else (
        set PYTHON=py
    )
) else (
    set PYTHON=python
)

echo Installing required packages...
%PYTHON% -m pip install numpy pandas matplotlib scikit-learn --quiet

echo.
echo Running climate prediction...
echo.

%PYTHON% simple_prediction.py

echo.
echo For full visualization, run:
echo %PYTHON% quick_test.py
echo.
pause
