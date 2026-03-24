Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== PC Optimizer - Build Script ===" -ForegroundColor Cyan
Write-Host ""

# Install PyInstaller if not present
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found - installing..." -ForegroundColor Yellow
    pip install pyinstaller
    Write-Host ""
}

# Build the exe
Write-Host "Building dist\PC-Optimizer.exe ..." -ForegroundColor Cyan
python -m PyInstaller optimizer.spec --clean --noconfirm

Write-Host ""
if (Test-Path "dist\PC-Optimizer.exe") {
    $size = [math]::Round((Get-Item "dist\PC-Optimizer.exe").Length / 1MB, 1)
    Write-Host "Done!  ->  dist\PC-Optimizer.exe  ($size MB)" -ForegroundColor Green
} else {
    Write-Host "Build failed - check output above for errors." -ForegroundColor Red
    exit 1
}
