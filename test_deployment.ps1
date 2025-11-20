#!/usr/bin/env pwsh
# Test deployment verification script

Write-Host "=== ChorePoints Deployment Verification ===" -ForegroundColor Cyan
Write-Host ""

# Test health check endpoint
Write-Host "Testing health check endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://elija-agota.azurewebsites.net/kid/health-check/" -Method Get -TimeoutSec 30
    Write-Host "✓ Health check successful!" -ForegroundColor Green
    Write-Host "  Status: $($response.status)" -ForegroundColor White
    Write-Host "  Version: $($response.version)" -ForegroundColor White
    Write-Host "  Timestamp: $($response.timestamp)" -ForegroundColor White
    Write-Host "  Message: $($response.message)" -ForegroundColor White
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test main page
Write-Host "Testing main page..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://elija-agota.azurewebsites.net/" -Method Get -TimeoutSec 30 -ErrorAction Stop
    Write-Host "✓ Main page accessible (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "✗ Main page failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Check Azure app status
Write-Host "Checking Azure app status..." -ForegroundColor Yellow
try {
    $appStatus = az webapp show --name elija-agota --resource-group chorepoints-rg-us --query "{state: state, location: location}" -o json | ConvertFrom-Json
    Write-Host "  State: $($appStatus.state)" -ForegroundColor White
    Write-Host "  Location: $($appStatus.location)" -ForegroundColor White
} catch {
    Write-Host "✗ Could not check Azure status" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "If health check shows old version, the deployment may not be working correctly." -ForegroundColor Yellow
Write-Host "Expected version: 2025.11.20-deployment-test" -ForegroundColor Cyan
