#Requires -Version 5.1
<#
  Run the Next.js frontend on Windows.
  Usage: powershell -ExecutionPolicy Bypass -File run-frontend.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$Root\frontend"
npm run dev
