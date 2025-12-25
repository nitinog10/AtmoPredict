# Direct CDS API Setup - No UID Required
Write-Host "Setting up CDS API configuration..." -ForegroundColor Cyan

$configPath = "$env:USERPROFILE\.cdsapirc"
$configContent = @"
url: https://cds.climate.copernicus.eu/api
key: 43dbfada-fcc1-4325-b033-0537ae3938b7
"@

try {
    $configContent | Out-File -FilePath $configPath -Encoding ascii -Force
    Write-Host "`n✅ CDS API configuration saved successfully!" -ForegroundColor Green
    Write-Host "Configuration file: $configPath" -ForegroundColor Yellow
    Write-Host "`nContent:" -ForegroundColor Cyan
    Write-Host $configContent
    Write-Host "`n✅ You can now run: python climate_prediction.py" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
