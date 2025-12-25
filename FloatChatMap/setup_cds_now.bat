@echo off
echo Setting up CDS API configuration...
echo.

set config_file=%USERPROFILE%\.cdsapirc

(
echo url: https://cds.climate.copernicus.eu/api
echo key: 43dbfada-fcc1-4325-b033-0537ae3938b7
) > "%config_file%"

if exist "%config_file%" (
    echo.
    echo SUCCESS! CDS API configuration saved to:
    echo %config_file%
    echo.
    echo Configuration:
    echo -------------------
    type "%config_file%"
    echo -------------------
    echo.
    echo You can now run: python climate_prediction.py
) else (
    echo ERROR: Failed to create configuration file
)

echo.
pause
