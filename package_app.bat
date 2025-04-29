@echo off
echo Enhanced Theme Studio - Packaging Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    goto :error
)

echo Step 1: Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo Step 2: Installing required packages...
pip install -U pip wheel setuptools build
pip install PyQt6 numpy pillow pyinstaller

echo Step 3: Creating app icon...
python create_icon_script.py

echo Step 4: Building Python package...
python -m build

echo Step 5: Creating executable with PyInstaller...
pyinstaller pyinstaller.spec

echo.
echo ========================================
echo Packaging complete!
echo.
echo Python package available in: dist/
echo Executable available in: dist/EnhancedThemeStudio/
echo.
echo To install the package locally:
echo pip install -e .
echo.
echo To run the executable:
echo dist\EnhancedThemeStudio\EnhancedThemeStudio.exe
echo ========================================

call venv\Scripts\deactivate.bat
goto :end

:error
echo An error occurred during packaging.
echo Please check the output above for more information.

:end
pause 