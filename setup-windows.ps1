#Requires -Version 5.1
<#
  Tax Shield - Windows setup (PowerShell)
  Run from the project root:  powershell -ExecutionPolicy Bypass -File setup-windows.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "==> Checking Python..." -ForegroundColor Cyan
try { py --version } catch { python --version }

Write-Host "==> Checking Node..." -ForegroundColor Cyan
node --version
npm --version

Write-Host "==> Backend: creating .venv..." -ForegroundColor Cyan
if (-not (Test-Path "backend\.venv")) {
  py -m venv backend\.venv
}
& "backend\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
deactivate

if (-not (Test-Path "backend\.env")) {
  Write-Host "==> Creating backend\.env from .env.example" -ForegroundColor Cyan
  Copy-Item backend\.env.example backend\.env
} else {
  Write-Host "==> backend\.env already exists, leaving it." -ForegroundColor Yellow
}

if (-not (Test-Path "backend\uploads")) {
  New-Item -ItemType Directory -Path "backend\uploads" | Out-Null
}

Write-Host "==> Frontend: npm install..." -ForegroundColor Cyan
Set-Location "$Root\frontend"
if (Test-Path ".next") { Remove-Item -Recurse -Force ".next" }
# If node_modules was copied from macOS it contains darwin binaries - reinstall.
npm install

Set-Location $Root
Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Backend : run-backend.ps1  (http://localhost:8000/docs)"
Write-Host "Frontend: open a second terminal -> cd frontend; npm run dev  (http://localhost:3000)"
Write-Host "MongoDB : install MongoDB 6+ for Windows or run: docker compose up -d mongodb"
