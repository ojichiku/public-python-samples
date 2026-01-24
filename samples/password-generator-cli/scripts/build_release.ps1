$ErrorActionPreference = "Stop"

param(
    [string]$AppName = "PasswordGeneratorCLI",
    [string]$ExeName = "passgen.exe",
    [switch]$SkipBuild,
    [switch]$Clean
)

function Invoke-CommandLine {
    param(
        [string[]]$Command,
        [string]$WorkingDirectory
    )

    Write-Host ">>> $($Command -join ' ')"
    Push-Location $WorkingDirectory
    try {
        & $Command[0] $Command[1..($Command.Length - 1)]
        if ($LASTEXITCODE -ne 0) {
            throw "[ERROR] command failed: $($Command -join ' ')"
        }
    } finally {
        Pop-Location
    }
}

function Get-DistDir {
    param(
        [string]$DistRoot
    )

    $candidates = Get-ChildItem -Path $DistRoot -Directory -Filter "*.dist" -ErrorAction SilentlyContinue
    if (-not $candidates) {
        throw "[ERROR] dist folder not found: $DistRoot"
    }
    if ($candidates.Count -gt 1) {
        $names = ($candidates | ForEach-Object { $_.Name }) -join ", "
        throw "[ERROR] multiple dist folders found: $names"
    }
    return $candidates[0].FullName
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Entry = Join-Path $RepoRoot "password_gen.py"
$DistRoot = Join-Path $RepoRoot "dist"
$OutputRoot = Join-Path $RepoRoot "release"
$ReleaseDir = Join-Path $OutputRoot $AppName
$AppDir = Join-Path $ReleaseDir "app"

if (Test-Path -Path $ReleaseDir) {
    if ($Clean) {
        Remove-Item -Path $ReleaseDir -Recurse -Force
    } else {
        throw "[ERROR] output already exists: $ReleaseDir"
    }
}

New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null

if (-not $SkipBuild) {
    $python = (Get-Command python).Source
    $command = @(
        $python,
        "-m",
        "nuitka",
        "--standalone",
        "--output-dir=$DistRoot",
        "--output-filename=$ExeName",
        $Entry
    )
    Invoke-CommandLine -Command $command -WorkingDirectory $RepoRoot
}

$distDir = Get-DistDir -DistRoot $DistRoot
Copy-Item -Path $distDir -Destination $AppDir -Recurse

$readme = Join-Path $OutputRoot "README.txt"
if (-not (Test-Path -Path $readme)) {
    throw "[ERROR] README.txt not found: $readme"
}
Copy-Item -Path $readme -Destination (Join-Path $ReleaseDir "README.txt")

$licenses = Join-Path $OutputRoot "LICENSES"
if (-not (Test-Path -Path $licenses)) {
    throw "[ERROR] LICENSES not found: $licenses"
}
Copy-Item -Path $licenses -Destination (Join-Path $ReleaseDir "LICENSES")

Write-Host "[OK] Release output: $ReleaseDir"
