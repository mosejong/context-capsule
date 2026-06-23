param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"

function Write-Step {
    param([string]$Message)
    Write-Host "[Context Capsule] $Message"
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
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        try {
            $version = & py -3.13 --version 2>$null
            if ($LASTEXITCODE -eq 0 -and $version -match "Python 3\.13") {
                return @("py", "-3.13")
            }
        } catch {
            # Fall back to python below.
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "Python 3.13 is required. Install Python 3.13 first, then run this script again."
    }

    $versionText = & python --version
    if ($versionText -notmatch "Python 3\.13") {
        throw "Python 3.13 is required. Current python reports: $versionText"
    }

    return @("python")
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

Set-Location $ProjectRoot

if (-not (Test-Path $VenvPython)) {
    if ($DryRun) {
        Write-Step "Dry-run: would locate Python 3.13"
    } else {
        $script:PythonCommand = Get-PythonCommand
        Write-Step "Using Python command: $($script:PythonCommand -join ' ')"
    }

    Invoke-IfNeeded "create virtual environment at .venv" {
        Invoke-Python @("-m", "venv", ".venv")
    }
} else {
    Write-Step "Virtual environment already exists."
}

if (-not (Test-Path $Requirements)) {
    throw "requirements.txt not found at $Requirements"
}

Invoke-IfNeeded "install runtime dependencies" {
    & $VenvPython -m pip install -r $Requirements
}

if ($DryRun) {
    Write-Step "Dry-run complete."
} else {
    Write-Step "Install complete."
}
Write-Step "Run .\run_context_capsule.bat or scripts\run_dashboard.ps1 to start the local dashboard."
