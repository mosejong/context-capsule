param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$MinimumPythonMajor = 3
$MinimumPythonMinor = 11

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

    throw "Python 3.11 or newer is required. Install Python 3.11+ first, then run this script again."
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

Set-Location $ProjectRoot

if (-not (Test-Path $VenvPython)) {
    if ($DryRun) {
        Write-Step "Dry-run: would locate Python 3.11 or newer"
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
