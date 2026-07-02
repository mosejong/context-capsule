param(
    [string]$Version = "0.2.16",
    [string]$OutputDir = "dist",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PackageName = "context-capsule-v$Version"
$DistDir = Join-Path $ProjectRoot $OutputDir
$ZipPath = Join-Path $DistDir "$PackageName.zip"

function Write-Step {
    param([string]$Message)
    Write-Host "[Context Capsule] $Message"
}

function Assert-RequiredFile {
    param([string]$RelativePath)
    $path = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path $path)) {
        throw "Required release file is missing: $RelativePath"
    }
}

function Assert-SafeOutputPath {
    param([string]$Path)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $distFullPath = [System.IO.Path]::GetFullPath($DistDir)
    if (-not $fullPath.StartsWith($distFullPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to write outside release output directory: $fullPath"
    }
}

Set-Location $ProjectRoot

$requiredFiles = @(
    "README.md",
    "START_HERE_KO.md",
    "LICENSE",
    "requirements.txt",
    "pyproject.toml",
    "run_context_capsule.bat",
    "context_capsule_cli.bat",
    "app\web\server.py",
    "app\web\static\index.html",
    "app\web\static\styles.css",
    "app\web\static\app.js",
    "scripts\install_windows.ps1",
    "scripts\run_dashboard.ps1",
    "scripts\context_capsule_cli.ps1",
    "docs\local_app.md",
    "docs\reference\token_evidence.md",
    "docs\reference\workflow_graph.md",
    "docs\reference\work_handoff_ownership.md",
    "docs\reference\project_health_check.md",
    "docs\operations\beta_feedback_loop.md",
    "docs\operations\release_packaging.md",
    "docs\presentation\target_positioning.md",
    "docs\presentation\demo_capture_flow.md",
    "docs\assets\screenshots\01_dashboard_first_screen.png",
    "docs\assets\screenshots\02_work_handoff_summary.png",
    "docs\assets\screenshots\03_metric_conflict_risk.png",
    "docs\releases\v$Version.md"
)

foreach ($file in $requiredFiles) {
    Assert-RequiredFile $file
}

$blockedTrackedPrefixes = @(
    ".venv/",
    "venv/",
    "env/",
    "outputs/",
    "dist/",
    "build/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "context_capsule.egg-info/"
)

$trackedFiles = & git ls-files
foreach ($file in $trackedFiles) {
    $normalized = $file.Replace("\", "/")
    foreach ($prefix in $blockedTrackedPrefixes) {
        if ($normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Release package would include generated/local file: $file"
        }
    }
}

$status = & git status --porcelain
if ($status) {
    Write-Step "Warning: working tree has uncommitted changes. git archive packages HEAD only."
}

Write-Step "Release package: $PackageName"
Write-Step "Output: $ZipPath"

if ($DryRun) {
    Write-Step "Dry-run complete. No ZIP was written."
    exit 0
}

New-Item -ItemType Directory -Force $DistDir | Out-Null
Assert-SafeOutputPath $ZipPath

if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

& git archive --format zip --output $ZipPath --prefix "$PackageName/" HEAD
if ($LASTEXITCODE -ne 0) {
    throw "git archive failed."
}

$zipItem = Get-Item $ZipPath
Write-Step "Wrote $($zipItem.FullName)"
Write-Step "Size: $([Math]::Round($zipItem.Length / 1MB, 2)) MB"

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
try {
    $entryNames = $zip.Entries | ForEach-Object { $_.FullName }
    $mustHave = @(
        "$PackageName/README.md",
        "$PackageName/START_HERE_KO.md",
        "$PackageName/run_context_capsule.bat",
        "$PackageName/context_capsule_cli.bat",
        "$PackageName/app/web/server.py",
        "$PackageName/app/web/static/index.html",
        "$PackageName/scripts/install_windows.ps1",
        "$PackageName/scripts/run_dashboard.ps1",
        "$PackageName/docs/releases/v$Version.md",
        "$PackageName/docs/reference/token_evidence.md",
        "$PackageName/docs/reference/workflow_graph.md",
        "$PackageName/docs/reference/work_handoff_ownership.md",
        "$PackageName/docs/reference/project_health_check.md",
        "$PackageName/docs/operations/beta_feedback_loop.md",
        "$PackageName/docs/assets/screenshots/01_dashboard_first_screen.png",
        "$PackageName/docs/assets/screenshots/02_work_handoff_summary.png",
        "$PackageName/docs/assets/screenshots/03_metric_conflict_risk.png"
    )
    foreach ($entry in $mustHave) {
        if ($entryNames -notcontains $entry) {
            throw "Release ZIP is missing expected entry: $entry"
        }
    }
} finally {
    $zip.Dispose()
}

Write-Step "Release ZIP verification passed."
