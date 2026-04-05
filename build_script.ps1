$ErrorActionPreference = "Stop"

Write-Host "Starting Windows build..."

# --- CONFIG ---
$APP_NAME = "markdown_analyzer"
$ENTRY_POINT = "application/main.py"
$REQUIREMENTS = "application/requirements.txt"
$VENV_DIR = "application/venv"
$ASSETS_DIR = "application/ui/assets"

# --- ENSURE ROOT ---
Set-Location -Path $PSScriptRoot
Write-Host "Working directory: $(Get-Location)"

# --- CREATE VENV ---
if (!(Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VENV_DIR
}

# --- ACTIVATE ---
Write-Host "Activating venv..."
& "$VENV_DIR\Scripts\Activate.ps1"

# --- INSTALL ---
pip install --upgrade pip
pip install -r $REQUIREMENTS
pip install pyinstaller

# --- CLEAN ---
Write-Host "Cleaning old builds..."
Remove-Item -Recurse -Force build, dist, *.spec -ErrorAction SilentlyContinue

# --- BUILD ---
Write-Host "Building executable..."

pyinstaller `
    --name $APP_NAME `
    --onefile `
    --noconfirm `
    --add-data "$ASSETS_DIR;application/ui/assets" `
    $ENTRY_POINT

Write-Host "Build finished."
Write-Host "Output: $(Get-Location)\dist\$APP_NAME.exe"

deactivate
