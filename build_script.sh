#!/bin/bash

set -e

echo "Starting Unix build..."

# --- CONFIG ---
APP_NAME="markdown_analyzer"
ENTRY_POINT="application/main.py"
REQUIREMENTS="application/requirements.txt"
VENV_DIR="application/venv"
ASSETS_DIR="application/ui/assets"

# --- ENSURE ROOT ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $(pwd)"

# --- CREATE VENV ---
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# --- ACTIVATE ---
echo "Activating venv..."
source "$VENV_DIR/bin/activate"

# --- INSTALL ---
pip install --upgrade pip
pip install -r "$REQUIREMENTS"
pip install pyinstaller

# --- CLEAN ---
echo "Cleaning old builds..."
rm -rf build dist *.spec

# --- BUILD ---
echo "Building executable..."

pyinstaller \
    --name "$APP_NAME" \
    --onefile \
    --noconfirm \
    --add-data "$ASSETS_DIR:application/ui/assets" \
    "$ENTRY_POINT"

echo "Build finished."
echo "Output: $(pwd)/dist/$APP_NAME"

deactivate
