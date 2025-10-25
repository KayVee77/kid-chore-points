# Dev helper script (PowerShell)
# Creates/activates venv, installs/updates deps, runs migrations, starts server, opens browser.

param(
	[switch]$Reset,
	[int]$Port = 8000
)

Write-Host "== Taškų Nuotykis dev start ==" -ForegroundColor Cyan

if ($Reset -and (Test-Path .venv)) {
	Write-Host "Removing existing venv (Reset requested)" -ForegroundColor Yellow
	Remove-Item -Recurse -Force .venv
}

if (-not (Test-Path .venv)) {
	Write-Host "Creating virtual environment" -ForegroundColor Green
	python -m venv .venv
	if ($LASTEXITCODE -ne 0) { exit 1 }
}

. .venv/Scripts/Activate.ps1

if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
	Write-Error "pip not available in venv"; exit 1
}

$reqFile = "requirements.txt"
$hashFile = ".venv/.req_hash"
if (Test-Path $reqFile) {
	$currentHash = (Get-FileHash $reqFile -Algorithm SHA256).Hash
	$storedHash = if (Test-Path $hashFile) { Get-Content $hashFile -ErrorAction SilentlyContinue } else { "" }
	if ($currentHash -ne $storedHash) {
		Write-Host "Installing / updating dependencies" -ForegroundColor Green
		pip install -r $reqFile
		if ($LASTEXITCODE -ne 0) { exit 1 }
		$currentHash | Out-File $hashFile -Encoding ascii -Force
	} else {
		Write-Host "Dependencies up to date" -ForegroundColor DarkGray
	}
}
else {
	Write-Warning "requirements.txt not found. Skipping dependency install."
}

Write-Host "Applying migrations" -ForegroundColor Green
python manage.py migrate
if ($LASTEXITCODE -ne 0) { exit 1 }

$url = "http://127.0.0.1:$Port/"
Write-Host "Opening $url" -ForegroundColor Cyan
Start-Process $url

Write-Host "Starting Django development server (CTRL+C to stop)" -ForegroundColor Green
python manage.py runserver 127.0.0.1:$Port
