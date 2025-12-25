# CDS API Setup Script
# Edit the UID below with your actual UID

# ⚠️ CHANGE THIS to your actual UID (the number before the colon in your CDS dashboard)
$UID = "YOUR_UID_HERE"

# Your provided credentials
$API_KEY = "fa8373b2-5bc8-4bc9-ad6b-829d482cb15c"
$URL = "https://cds.climate.copernicus.eu/api"

# Check if UID was changed
if ($UID -eq "YOUR_UID_HERE") {
    Write-Host "ERROR: You need to edit this file first!" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Edit this file (setup_cds_with_uid.ps1)" -ForegroundColor Yellow
    Write-Host "2. Change YOUR_UID_HERE to your actual UID number" -ForegroundColor Yellow
    Write-Host "3. Save and run again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To find your UID:" -ForegroundColor Cyan
    Write-Host "- Go to https://cds.climate.copernicus.eu/api-how-to"
    Write-Host "- Look for 'key: UID:API-KEY' format"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

# Create the config file
$configPath = "$env:USERPROFILE\.cdsapirc"
$configContent = @"
url: $URL
key: ${UID}:${API_KEY}
"@

try {
    $configContent | Out-File -FilePath $configPath -Encoding ascii
    Write-Host "✅ CDS API configuration saved successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration saved to: $configPath" -ForegroundColor Cyan
    Write-Host "URL: $URL"
    Write-Host "UID: $UID"
    Write-Host "API Key: $($API_KEY.Substring(0,8))...$($API_KEY.Substring($API_KEY.Length-4))"
    Write-Host ""
    Write-Host "✅ You can now run: python climate_prediction.py" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error saving configuration: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
