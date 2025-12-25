@echo off
echo CDS API Configuration Setup
echo ==========================
echo.
echo This will help you create the .cdsapirc configuration file
echo.

set /p uid="Enter your CDS UID: "
set /p apikey="Enter your CDS API Key: "

if "%uid%"=="" (
    echo ERROR: UID cannot be empty!
    pause
    exit /b 1
)

if "%apikey%"=="" (
    echo ERROR: API Key cannot be empty!
    pause
    exit /b 1
)

set config_path=%USERPROFILE%\.cdsapirc

echo.
echo Creating config file at: %config_path%

(
echo url: https://cds.climate.copernicus.eu/api/v2
echo key: %uid%:%apikey%
) > "%config_path%"

echo.
echo ✓ Configuration file created successfully!
echo.
echo You can now run: python climate_prediction.py
echo to download real climate data from CDS
echo.
pause
