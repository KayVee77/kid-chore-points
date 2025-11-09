# Script to deploy updated chores and rewards CSV files to Azure
# Run this after updating chores.csv or rewards.csv

Write-Host "`n=== ChorePoints CSV Deployment ===" -ForegroundColor Cyan

# Deploy chores.csv
Write-Host "`nDeploying chores.csv..." -ForegroundColor Yellow
& "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" webapp deploy `
    --resource-group chorepoints-rg-us `
    --name elija-agota `
    --src-path "initial_data/chores.csv" `
    --target-path "initial_data/chores.csv" `
    --type static

# Deploy rewards.csv
Write-Host "`nDeploying rewards.csv..." -ForegroundColor Yellow
& "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" webapp deploy `
    --resource-group chorepoints-rg-us `
    --name elija-agota `
    --src-path "initial_data/rewards.csv" `
    --target-path "initial_data/rewards.csv" `
    --type static

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. SSH into Azure: az webapp ssh --name elija-agota --resource-group chorepoints-rg-us"
Write-Host "2. Reload data: python manage.py load_initial_data"
Write-Host "`n"
