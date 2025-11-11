# Dev helper script (PowerShell)
# Creates/activates venv, installs/updates deps, runs migrations, starts server, opens browser.

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
        [switch]$Reset,
        [switch]$ForceReset,
        [int]$Port = 8000
)

$script:ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) {
        $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

Push-Location $ScriptRoot
try {

        Write-Host "== Taškų Nuotykis dev start ==" -ForegroundColor Cyan

        if ($Reset -and -not $ForceReset) {
                Write-Warning "-Reset requested but not confirmed. To rebuild from scratch run: ./dev.ps1 -Reset -ForceReset"
                Write-Host "Continuing without resetting to preserve the current virtual environment and SQLite data." -ForegroundColor DarkYellow
                $Reset = $false
        }

        $venvPath = Join-Path $ScriptRoot '.venv'
        if ($Reset -and (Test-Path $venvPath)) {
                Write-Host "Reset requested: the virtual environment at $venvPath would be removed." -ForegroundColor Yellow
                Write-Host "SQLite (db.sqlite3) and any other data files are preserved." -ForegroundColor DarkGray
                if ($PSCmdlet.ShouldProcess($venvPath, 'Remove development virtual environment (.venv)')) {
                        Write-Host "Removing existing venv (Reset confirmed)" -ForegroundColor Yellow
                        Remove-Item -Recurse -Force $venvPath
                        Write-Host "Existing db.sqlite3 (and any other data files) are left untouched." -ForegroundColor DarkGray
                }
                else {
                        Write-Host "Reset cancelled. Continuing with existing environment." -ForegroundColor DarkYellow
                        $Reset = $false
                }
        }

        if (-not (Test-Path $venvPath)) {
                Write-Host "Creating virtual environment" -ForegroundColor Green
                python -m venv $venvPath
                if ($LASTEXITCODE -ne 0) { exit 1 }
        }

        . (Join-Path $venvPath 'Scripts/Activate.ps1')

        if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
                Write-Error "pip not available in venv"; exit 1
        }

        $reqFile = "requirements.txt"
        $hashFile = Join-Path $venvPath '.req_hash'
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
}
finally {
        Pop-Location
}
