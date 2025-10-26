# HTTPS run script (PowerShell)
# Activates existing venv and starts Django server with HTTPS support
# Requires django-extensions and SSL certificates

param(
	[int]$Port = 8000
)

Write-Host "== Taškų Nuotykis HTTPS Development Server ==" -ForegroundColor Cyan

# Get the script directory and set paths relative to it
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"
$CertPath = Join-Path $ScriptDir "ssl\cert.pem"
$KeyPath = Join-Path $ScriptDir "ssl\key.pem"

# Check if venv exists
if (-not (Test-Path $VenvPath)) {
	Write-Error "Virtual environment not found. Run ./chorepoints/dev.ps1 first to set up the project."
	exit 1
}

# Check if SSL certificates exist
if (-not (Test-Path $CertPath) -or -not (Test-Path $KeyPath)) {
	Write-Host "SSL certificates not found. Generating them now..." -ForegroundColor Yellow
	Set-Location $ScriptDir
	python generate_cert.py
	Write-Host ""
}

# Activate venv
Write-Host "Activating virtual environment" -ForegroundColor Green
. (Join-Path $VenvPath "Scripts\Activate.ps1")

# Get local IP address for network access
$LocalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
	$_.InterfaceAlias -like '*Wi-Fi*' -and 
	$_.PrefixOrigin -eq 'Dhcp'
} | Select-Object -First 1).IPAddress

# If no Wi-Fi DHCP, try Ethernet
if (-not $LocalIP) {
	$LocalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
		$_.InterfaceAlias -like '*Ethernet*' -and 
		$_.PrefixOrigin -eq 'Dhcp'
	} | Select-Object -First 1).IPAddress
}

# Open browser
$url = "https://127.0.0.1:$Port/"
Write-Host "Opening $url" -ForegroundColor Cyan
Write-Host "(You may need to accept the security warning in your browser)" -ForegroundColor DarkYellow
Start-Process $url

# Change to chorepoints directory where manage.py is located
Set-Location $ScriptDir

# Start server with HTTPS
Write-Host ""
Write-Host "Starting Django HTTPS development server (CTRL+C to stop)" -ForegroundColor Green
Write-Host "Local access: https://127.0.0.1:$Port/" -ForegroundColor Yellow
if ($LocalIP) {
	Write-Host "Network access: https://${LocalIP}:$Port/" -ForegroundColor Yellow
	Write-Host ""
	Write-Host "Mobile Instructions:" -ForegroundColor Cyan
	Write-Host "   1. Open https://${LocalIP}:$Port/ on your phone" -ForegroundColor White
	Write-Host "   2. Accept/Proceed through security warning (self-signed cert)" -ForegroundColor White
	Write-Host "   3. App should work with HTTPS!" -ForegroundColor White
}
Write-Host ""
Write-Host "Tip: Use ./chorepoints/dev.ps1 for package updates or migrations" -ForegroundColor DarkGray
Write-Host ""

# Use runserver_plus from django-extensions with SSL
python manage.py runserver_plus --cert-file ssl/cert.pem --key-file ssl/key.pem 0.0.0.0:$Port
