param(
    [int]$Port = 8501,
    [switch]$NoInstall,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$InstallScript = Join-Path $PSScriptRoot "install_windows.ps1"
$LogDir = Join-Path $ProjectRoot "outputs\logs"
$LogPath = Join-Path $LogDir ("dashboard_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

function Write-Step {
    param([string]$Message)
    Write-Host "[Context Capsule] $Message"
    Write-Log "[Context Capsule] $Message"
}

function Write-Log {
    param([string]$Message)
    if ($DryRun) {
        return
    }
    if (Test-Path $LogDir) {
        Add-Content -Path $LogPath -Value $Message -Encoding UTF8
    }
}

function Initialize-Log {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force $LogDir | Out-Null
        Set-Content -Path $LogPath -Value "[Context Capsule] dashboard log started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Encoding UTF8
    }
}

function Write-FailureGuide {
    param([object]$ErrorRecord)

    Write-Host ""
    Write-Host "[Context Capsule] 실행 중 문제가 발생했습니다." -ForegroundColor Red
    Write-Host "로그 파일: $LogPath"
    Write-Host ""
    Write-Host "먼저 확인할 것:"
    Write-Host "1. ZIP 압축을 완전히 푼 폴더에서 실행했는지 확인하세요."
    Write-Host "2. Python 3.11 이상이 설치되어 있는지 확인하세요."
    Write-Host "3. 포트 8501이 이미 사용 중이면 scripts\run_dashboard.ps1 -Port 8502 로 실행해보세요."
    Write-Host "4. 그래도 막히면 outputs\logs 폴더의 최신 dashboard 로그를 피드백과 함께 보내주세요."
    Write-Host ""
    Write-Host "도움말: START_HERE_KO.md 또는 docs\local_app.md"
    Write-Log "[ERROR] $($ErrorRecord.Exception.Message)"
}

try {
    Initialize-Log
    Set-Location $ProjectRoot
    Write-Step "Project root: $ProjectRoot"
    if (-not $DryRun) {
        Write-Step "Log file: $LogPath"
    }

    if (-not (Test-Path $VenvPython)) {
        if ($NoInstall) {
            throw ".venv를 찾을 수 없습니다. scripts\install_windows.ps1을 먼저 실행하거나 -NoInstall 옵션을 빼고 실행하세요."
        }

        Write-Step "Virtual environment not found. Installing runtime first."
        if ($DryRun) {
            Write-Step "Dry-run: would call scripts\install_windows.ps1"
        } else {
            & $InstallScript
            if (-not $?) {
                throw "설치 스크립트가 실패했습니다."
            }
        }
    }

    $command = @(
        "-m", "uvicorn", "app.web.server:app",
        "--host", "localhost",
        "--port", "$Port"
    )

    Write-Step "Starting FastAPI local UI at http://localhost:$Port"
    if ($DryRun) {
        Write-Step "Dry-run: $VenvPython $($command -join ' ')"
        exit 0
    }

    & $VenvPython @command
    if ($LASTEXITCODE -ne 0) {
        throw "로컬 웹 UI 실행에 실패했습니다."
    }
} catch {
    Write-FailureGuide $_
    exit 1
}
