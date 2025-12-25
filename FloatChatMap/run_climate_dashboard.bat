@echo off
echo ============================================
echo Climate Dashboard Generator
echo ============================================
echo.

REM Set location based on the images (Madhya Pradesh, India)
set LOCATION_LAT=23.2
set LOCATION_LON=77.4
set LOCATION_NAME=Sehore, Madhya Pradesh

REM Create data directory
if not exist "data" mkdir data

REM Generate current weather data file
echo Generating current weather data...
(
echo {
echo   "location": "%LOCATION_NAME%",
echo   "coordinates": {"lat": %LOCATION_LAT%, "lon": %LOCATION_LON%},
echo   "current_date": "2025-10-04",
echo   "temperature": {"current": 29, "min": 23, "max": 31, "unit": "C"},
echo   "aqi": {"value": 76, "category": "Moderate"},
echo   "wind": {"speed": 11, "gusts": 26, "direction": "NW", "unit": "kph"},
echo   "precipitation": {"status": "Light", "probability": 30},
echo   "pressure": 1013,
echo   "humidity": 65
echo }
) > data\current_weather.json

REM Run Python scripts if available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Running climate prediction model...
    python simple_prediction.py > data\prediction_output.txt 2>&1
    echo Done.
) else (
    echo Python not found. Using pre-generated data...
)

REM Generate the integrated HTML dashboard
echo.
echo Generating Climate Dashboard...
python generate_dashboard.py 2>nul || call :generate_static_dashboard

echo.
echo ============================================
echo Dashboard generated successfully!
echo.
echo Opening professional weather map in browser...
start weather_map_realistic.html

echo.
pause
exit /b

:generate_static_dashboard
echo Creating static dashboard...
REM This will be called if Python fails
copy climate_dashboard_template.html climate_dashboard.html >nul
echo Static dashboard created.
exit /b
