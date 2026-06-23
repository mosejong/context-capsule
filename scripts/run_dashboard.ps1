param(
    [int]$Port = 8501,
    [switch]$NoInstall,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$InstallScript = Join-Path $PSScriptRoot "install_windows.ps1"

function Write-Step {
    param([string]$Message)
    Write-Host "[Context Capsule] $Message"
}

Set-Location $ProjectRoot

if (-not (Test-Path $VenvPython)) {
    if ($NoInstall) {
        throw ".venv was not found. Run scripts\install_windows.ps1 first or remove -NoInstall."
    }

    Write-Step "Virtual environment not found. Installing runtime first."
    if ($DryRun) {
        Write-Step "Dry-run: would call scripts\install_windows.ps1"
    } else {
        & $InstallScript
    }
}

$command = @(
    "-m", "streamlit", "run", "app\main.py",
    "--server.address", "localhost",
    "--server.port", "$Port",
    "--browser.gatherUsageStats", "false"
)

Write-Step "Starting local dashboard at http://localhost:$Port"
if ($DryRun) {
    Write-Step "Dry-run: $VenvPython $($command -join ' ')"
    exit 0
}

& $VenvPython @command
