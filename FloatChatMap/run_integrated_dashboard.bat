@echo off
cls
echo ================================================================
echo       INTEGRATED CLIMATE DASHBOARD WITH WEATHER HEATMAPS
echo ================================================================
echo.
echo This integrated dashboard provides:
echo.
echo [1] CLIMATE ANALYSIS:
echo     - Search any location by coordinates
echo     - View historical climate trends (2015-2025)
echo     - See predictions for 2026
echo     - Interactive charts and graphs
echo.
echo [2] WEATHER HEATMAPS (NEW!):
echo     - Click "Weather Heatmaps" button
echo     - Opens professional weather visualization
echo     - Temperature, Wind, Precipitation, AQI layers
echo     - Real-time weather data
echo.
echo ================================================================
echo.
echo Opening integrated dashboard...
timeout /t 2 /nobreak >nul
start climate_dashboard_interactive.html
echo.
echo ================================================================
echo Dashboard opened successfully!
echo.
echo HOW TO USE:
echo 1. Enter coordinates or click on map to select location
echo 2. Click "Update Dashboard" to see climate analysis
echo 3. Click "Weather Heatmaps" to view live weather layers
echo 4. Switch between Temperature, Wind, Precipitation, AQI
echo 5. Use ESC or X button to close weather map
echo.
echo ================================================================
echo.
pause
