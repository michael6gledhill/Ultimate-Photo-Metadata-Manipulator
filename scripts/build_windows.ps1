# PowerShell build script for Windows
# Packages PhotoMetadataManipulator into a standalone .exe using PyInstaller
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 [-DistDir dist] [-Debug] [-Verbose]

param(
  [string]$DistDir = "dist",
  [switch]$Debug,
  [switch]$Verbose
)

$ErrorActionPreference = "Stop"

$AppName   = "PhotoMetadataManipulator"
$Entry     = "src/main.py"
$IconPath  = "logo.ico"   # Optional; place a logo.ico in project root

# Resolve project root (script's parent folder's parent)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Install Python 3.11/3.12 and ensure it's on PATH."
  }
}

# Check PyInstaller
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Error "PyInstaller not found. Install with: pip install pyinstaller"
}

# Verify entrypoint exists
if (-not (Test-Path $Entry)) {
  Write-Error "Entrypoint $Entry not found. Run this from the project root. Current: $(Get-Location)"
}

# Windowed vs console
$WindowFlag = if ($Debug -or $env:DEBUG_BUILD -eq '1') { "--console" } else { "--windowed" }
if ($Debug) { Write-Host "Debug build: console enabled." }

# Optional icon
$IconArg = @()
if (Test-Path $IconPath) { $IconArg = @('--icon', $IconPath) }
else { Write-Host "No logo.ico found. Continuing without custom icon." }

# Hidden imports only if installed (libxmp is optional)
$HiddenArgs = @()
$mods = & python -c "import importlib.util as u; mods=['piexif','libxmp']; print('\n'.join(m for m in mods if u.find_spec(m) is not None))" 2>$null
if ($LASTEXITCODE -eq 0 -and $mods) {
  $mods -split "`n" | ForEach-Object { if ($_ -ne '') { $HiddenArgs += @('--hidden-import', $_) } }
}

# Add src to module search paths so PyInstaller can find local modules
$PathsArgs = @('--paths', 'src')

# Dist/work directories
$OutDir = Join-Path $DistDir 'windows'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$WorkDir = 'build-windows'

# On Windows, --add-data uses a semicolon separator
$AddData = "src;src"

# Build using CLI (Windows cannot reuse the macOS .spec with BUNDLE)
$baseArgs = @(
  '--noconfirm',
  '--clean',
  '--distpath', $OutDir,
  '--workpath', $WorkDir,
  '--name', $AppName,
  $WindowFlag
)

if ($Verbose -or $env:VERBOSE -eq '1') { $baseArgs += @('--log-level','DEBUG') }
if ($IconArg.Count -gt 0) { $baseArgs += $IconArg }
if ($HiddenArgs.Count -gt 0) { $baseArgs += $HiddenArgs }
$baseArgs += $PathsArgs
$baseArgs += @($Entry)

Write-Host "==> Building Windows exe -> $OutDir" 
pyinstaller @baseArgs

Write-Host "==> Build complete. Inspect $OutDir"
$exePath = Join-Path $OutDir ("$AppName.exe")
if (Test-Path $exePath) {
  Write-Host "Executable: $exePath"
} else {
  Write-Warning "Executable not found. Check PyInstaller logs above."
}

Write-Host "Run the exe for logs: $exePath"
if (-not $Debug) {
  Write-Host "Tip: add -Debug to show console window during debugging."
}
