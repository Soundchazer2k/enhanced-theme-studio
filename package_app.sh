#!/bin/bash
echo "Enhanced Theme Studio - Packaging Script"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Step 2: Installing required packages..."
pip install -U pip wheel setuptools build
pip install PyQt6 numpy pillow pyinstaller

echo "Step 3: Creating app icon..."
python create_icon_script.py

echo "Step 4: Building Python package..."
python -m build

echo "Step 5: Creating executable with PyInstaller..."
pyinstaller pyinstaller.spec

echo
echo "========================================"
echo "Packaging complete!"
echo
echo "Python package available in: dist/"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Executable available in: dist/EnhancedThemeStudio.app"
    echo
    echo "To run the executable:"
    echo "open dist/EnhancedThemeStudio.app"
else
    echo "Executable available in: dist/EnhancedThemeStudio/"
    echo
    echo "To run the executable:"
    echo "./dist/EnhancedThemeStudio/EnhancedThemeStudio"
fi
echo
echo "To install the package locally:"
echo "pip install -e ."
echo "========================================"

deactivate 