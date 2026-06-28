param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$LogDir = Join-Path $ProjectRoot "outputs\logs"
$LogPath = Join-Path $LogDir ("install_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$MinimumPythonMajor = 3
$MinimumPythonMinor = 11

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
        Set-Content -Path $LogPath -Value "[Context Capsule] install log started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Encoding UTF8
    }
}

function Write-FailureGuide {
    param([object]$ErrorRecord)

    Write-Host ""
    Write-Host "[Context Capsule] 설치 중 문제가 발생했습니다." -ForegroundColor Red
    Write-Host "로그 파일: $LogPath"
    Write-Host ""
    Write-Host "먼저 확인할 것:"
    Write-Host "1. Python 3.11 이상이 설치되어 있는지 확인하세요."
    Write-Host "2. ZIP 압축을 완전히 푼 폴더에서 실행했는지 확인하세요."
    Write-Host "3. 인터넷 연결이 되는지 확인하세요. 첫 설치 때는 pip 패키지를 받아야 합니다."
    Write-Host "4. 그래도 막히면 outputs\logs 폴더의 최신 install 로그를 피드백과 함께 보내주세요."
    Write-Host ""
    Write-Host "도움말: START_HERE_KO.md 또는 docs\local_app.md"
    Write-Log "[ERROR] $($ErrorRecord.Exception.Message)"
}

function Invoke-IfNeeded {
    param(
        [string]$Description,
        [scriptblock]$Action
    )

    if ($DryRun) {
        Write-Step "Dry-run: would $Description"
    } else {
        Write-Step $Description
        & $Action
    }
}

function Get-PythonCommand {
    $candidates = @()
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $candidates += ,@("py", "-3.13")
        $candidates += ,@("py", "-3.12")
        $candidates += ,@("py", "-3.11")
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $candidates += ,@("python")
    }

    foreach ($candidate in $candidates) {
        $exe = $candidate[0]
        $prefixArgs = @()
        if ($candidate.Count -gt 1) {
            $prefixArgs = $candidate[1..($candidate.Count - 1)]
        }
        try {
            $versionText = & $exe @prefixArgs --version 2>$null
            if ($LASTEXITCODE -eq 0 -and (Test-SupportedPythonVersion $versionText)) {
                return $candidate
            }
        } catch {
            # Try the next candidate.
        }
    }

    throw "Python 3.11 이상을 찾지 못했습니다. Python 3.11 이상을 설치한 뒤 다시 실행하세요."
}

function Test-SupportedPythonVersion {
    param([string]$VersionText)
    if ($VersionText -notmatch "Python\s+(\d+)\.(\d+)") {
        return $false
    }
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    return ($major -gt $MinimumPythonMajor) -or ($major -eq $MinimumPythonMajor -and $minor -ge $MinimumPythonMinor)
}

function Invoke-Python {
    param([string[]]$Arguments)
    $exe = $script:PythonCommand[0]
    $prefixArgs = @()
    if ($script:PythonCommand.Count -gt 1) {
        $prefixArgs = $script:PythonCommand[1..($script:PythonCommand.Count - 1)]
    }
    & $exe @prefixArgs @Arguments
}

try {
    Initialize-Log
    Set-Location $ProjectRoot
    Write-Step "Project root: $ProjectRoot"
    if (-not $DryRun) {
        Write-Step "Log file: $LogPath"
    }

    if (-not (Test-Path $VenvPython)) {
        if ($DryRun) {
            Write-Step "Dry-run: would locate Python 3.11 or newer"
        } else {
            $script:PythonCommand = Get-PythonCommand
            Write-Step "Using Python command: $($script:PythonCommand -join ' ')"
        }

        Invoke-IfNeeded "create virtual environment at .venv" {
            Invoke-Python @("-m", "venv", ".venv")
            if ($LASTEXITCODE -ne 0) {
                throw "가상환경 생성에 실패했습니다."
            }
        }
    } else {
        Write-Step "Virtual environment already exists."
    }

    if (-not (Test-Path $Requirements)) {
        throw "requirements.txt를 찾을 수 없습니다: $Requirements"
    }

    Invoke-IfNeeded "install runtime dependencies" {
        & $VenvPython -m pip install -r $Requirements
        if ($LASTEXITCODE -ne 0) {
            throw "런타임 의존성 설치에 실패했습니다."
        }
    }

    if ($DryRun) {
        Write-Step "Dry-run complete."
    } else {
        Write-Step "Install complete."
    }
    Write-Step "Run .\run_context_capsule.bat or scripts\run_dashboard.ps1 to start the local dashboard."
} catch {
    Write-FailureGuide $_
    exit 1
}
