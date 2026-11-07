Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting TaxSahayak Development Servers (Local PWA)      " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; uvicorn backend.app.main:app --reload --port 8000"

# 2. Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "Backend running on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Frontend running on http://localhost:5173" -ForegroundColor Green
Write-Host "Swagger Docs on http://127.0.0.1:8000/docs" -ForegroundColor Cyan

