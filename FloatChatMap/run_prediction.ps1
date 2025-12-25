# Climate Prediction PowerShell Script

Write-Host "======================================"
Write-Host "Climate Prediction for October 4, 2026" -ForegroundColor Cyan
Write-Host "======================================"
Write-Host ""

# Check if Python is available
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Found Python: " -NoNewline
& $pythonCmd --version

# Install basic requirements
Write-Host "`nInstalling required packages..." -ForegroundColor Yellow
& $pythonCmd -m pip install numpy pandas matplotlib scikit-learn --quiet

# Run the simple prediction
Write-Host "`nRunning climate prediction..." -ForegroundColor Green
Write-Host ""
& $pythonCmd simple_prediction.py

Write-Host "`n`nFor full visualization with graphs, run:" -ForegroundColor Yellow
Write-Host "  $pythonCmd quick_test.py"
Write-Host ""
Read-Host "Press Enter to exit"
