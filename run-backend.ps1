#Requires -Version 5.1
<#
  Run the FastAPI backend on Windows.
  Usage: powershell -ExecutionPolicy Bypass -File run-backend.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$Root\backend"
& ".\.venv\Scripts\Activate.ps1"
$env:MONGODB_URL = $env:MONGODB_URL  # uses backend\.env via pydantic-settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
