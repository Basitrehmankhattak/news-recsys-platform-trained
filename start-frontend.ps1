# Start Frontend Application
Write-Host " Starting Frontend Application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
streamlit run app.py
