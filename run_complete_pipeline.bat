@echo off
echo ======================================================================
echo    EXTREME WEATHER PREDICTION - COMPLETE PIPELINE
echo ======================================================================
echo.

echo Step 1: Collecting NASA Data for Multiple Cities...
echo ======================================================================
python src\data_collection.py --multi
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Data collection failed!
    pause
    exit /b 1
)
echo.
echo ✓ Data collection completed!
echo.

echo Step 2: Feature Engineering...
echo ======================================================================
python src\feature_engineering.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Feature engineering failed!
    pause
    exit /b 1
)
echo.
echo ✓ Feature engineering completed!
echo.

echo Step 3: Training Models...
echo ======================================================================
python src\train_models.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Model training failed!
    pause
    exit /b 1
)
echo.
echo ✓ Model training completed!
echo.

echo Step 4: Evaluating Models...
echo ======================================================================
python src\evaluate.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Model evaluation failed!
    pause
    exit /b 1
)
echo.
echo ✓ Model evaluation completed!
echo.

echo ======================================================================
echo    ✅ PIPELINE COMPLETED SUCCESSFULLY!
echo ======================================================================
echo.
echo Next steps:
echo   1. Check trained models in: models\trained\
echo   2. View evaluation results in: evaluation_results\
echo   3. Start the API server: python src\api.py
echo   4. Open frontend: frontend\index.html
echo.
pause

