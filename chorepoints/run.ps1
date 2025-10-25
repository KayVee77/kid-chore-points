# Quick run script (PowerShell)
# Activates existing venv and starts Django server
# Use dev.ps1 for initial setup or when dependencies change

param(
	[int]$Port = 8000
)

Write-Host "== Taškų Nuotykis quick start ==" -ForegroundColor Cyan

# Check if venv exists
if (-not (Test-Path .venv)) {
	Write-Error "Virtual environment not found. Run ./dev.ps1 first to set up the project."
	exit 1
}

# Activate venv
Write-Host "Activating virtual environment" -ForegroundColor Green
. .venv/Scripts/Activate.ps1

# Open browser
$url = "http://127.0.0.1:$Port/"
Write-Host "Opening $url" -ForegroundColor Cyan
Start-Process $url

# Start server
Write-Host "Starting Django development server (CTRL+C to stop)" -ForegroundColor Green
Write-Host "Tip: Use ./dev.ps1 if you need to install/update packages or run migrations" -ForegroundColor DarkGray
python manage.py runserver 127.0.0.1:$Port
