param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$InstallScript = Join-Path $PSScriptRoot "install_windows.ps1"

Set-Location $ProjectRoot

if (-not (Test-Path $VenvPython)) {
    Write-Host "[Context Capsule] Virtual environment not found. Installing runtime first."
    & $InstallScript
}

& $VenvPython -m app.cli @CliArgs
