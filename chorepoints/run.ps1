# Quick run script (PowerShell)
# Activates existing venv and starts Django server
# Use dev.ps1 for initial setup or when dependencies change

param(
	[int]$Port = 8000
)

Write-Host "== Taškų Nuotykis quick start ==" -ForegroundColor Cyan

# Get the script directory and set paths relative to it
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"

# Check if venv exists
if (-not (Test-Path $VenvPath)) {
	Write-Error "Virtual environment not found. Run ./chorepoints/dev.ps1 first to set up the project."
	exit 1
}

# Activate venv
Write-Host "Activating virtual environment" -ForegroundColor Green
. (Join-Path $VenvPath "Scripts\Activate.ps1")

# Get local IP address for network access
$LocalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*' -or $_.InterfaceAlias -like '*Ethernet*'} | Select-Object -First 1).IPAddress

# Open browser
$url = "http://127.0.0.1:$Port/"
Write-Host "Opening $url" -ForegroundColor Cyan
Start-Process $url

# Change to chorepoints directory where manage.py is located
Set-Location $ScriptDir

# Start server with network access
Write-Host "Starting Django development server (CTRL+C to stop)" -ForegroundColor Green
Write-Host "Local access: http://127.0.0.1:$Port/" -ForegroundColor Yellow
if ($LocalIP) {
	Write-Host "Network access: http://${LocalIP}:$Port/" -ForegroundColor Yellow
}
Write-Host "Tip: Use ./chorepoints/dev.ps1 if you need to install/update packages or run migrations" -ForegroundColor DarkGray
python manage.py runserver 0.0.0.0:$Port
