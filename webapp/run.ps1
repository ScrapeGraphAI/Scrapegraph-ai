param(
    [ValidateSet('backend','frontend','all')]
    [string]$Mode = 'all'
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

function Start-Backend {
    Write-Host "Starting backend (FastAPI)..." -ForegroundColor Green
    Push-Location $BackendDir
    try {
        & "C:\Users\Ege\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    }
    finally {
        Pop-Location
    }
}

function Start-Frontend {
    Write-Host "Starting frontend (React + Vite)..." -ForegroundColor Cyan
    Push-Location $FrontendDir
    try {
        npm run dev
    }
    finally {
        Pop-Location
    }
}

switch ($Mode) {
    'backend' { Start-Backend }
    'frontend' { Start-Frontend }
    'all' {
        $job1 = Start-Job -ScriptBlock { param($d) Set-Location $d; & "C:\Users\Ege\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 } -ArgumentList $BackendDir
        $job2 = Start-Job -ScriptBlock { param($d) Set-Location $d; npm run dev } -ArgumentList $FrontendDir

        Write-Host "Listening:" -ForegroundColor Yellow
        Write-Host "  Backend  -> http://127.0.0.1:8000/docs" -ForegroundColor Cyan
        Write-Host "  Frontend -> http://127.0.0.1:5173" -ForegroundColor Cyan
        Write-Host "Press any key to stop all services" -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

        $job1, $job2 | Stop-Job -PassThru | Remove-Job
    }
}
