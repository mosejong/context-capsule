param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$InstallScript = Join-Path $PSScriptRoot "install_windows.ps1"
$LogDir = Join-Path $ProjectRoot "outputs\logs"
$LogPath = Join-Path $LogDir ("cli_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

function Write-Step {
    param([string]$Message)
    Write-Log "[Context Capsule] $Message"
}

function Write-Log {
    param([string]$Message)
    if (Test-Path $LogDir) {
        Add-Content -Path $LogPath -Value $Message -Encoding UTF8
    }
}

function Initialize-Log {
    New-Item -ItemType Directory -Force $LogDir | Out-Null
    Set-Content -Path $LogPath -Value "[Context Capsule] CLI log started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Encoding UTF8
}

function Write-FailureGuide {
    param([object]$ErrorRecord)

    Write-Host ""
    Write-Host "[Context Capsule] CLI 실행 중 문제가 발생했습니다." -ForegroundColor Red
    Write-Host "로그 파일: $LogPath"
    Write-Host ""
    Write-Host "먼저 확인할 것:"
    Write-Host "1. run_context_capsule.bat으로 대시보드가 켜지는지 확인하세요."
    Write-Host "2. Python 3.11 이상과 .venv 설치가 정상인지 확인하세요."
    Write-Host "3. 그래도 막히면 outputs\logs 폴더의 최신 cli 로그를 피드백과 함께 보내주세요."
    Write-Host ""
    Write-Host "도움말: START_HERE_KO.md 또는 docs\local_app.md"
    Write-Log "[ERROR] $($ErrorRecord.Exception.Message)"
}

try {
    Initialize-Log
    Set-Location $ProjectRoot
    Write-Step "Project root: $ProjectRoot"
    Write-Step "Log file: $LogPath"

    if (-not (Test-Path $VenvPython)) {
        Write-Step "Virtual environment not found. Installing runtime first."
        & $InstallScript
        if (-not $?) {
            throw "설치 스크립트가 실패했습니다."
        }
    }

    & $VenvPython -m app.cli @CliArgs
    exit $LASTEXITCODE
} catch {
    Write-FailureGuide $_
    exit 1
}
