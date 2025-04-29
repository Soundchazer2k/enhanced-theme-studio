@echo off
echo Enhanced Theme Studio - Packaging Script (Debug Version)
echo =========================================================
echo.

REM Create a log file
set LOGFILE=package_debug_log.txt
echo Packaging started at %date% %time% > %LOGFILE%

echo Checking prerequisites...
echo Checking prerequisites... >> %LOGFILE%

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo ERROR: Python is not installed or not in PATH >> %LOGFILE%
    goto :error
)

REM Get Python version
python --version >> %LOGFILE% 2>&1
echo Python found.

REM Check if folder structure exists
if not exist "enhanced_theme_generator.py" (
    echo ERROR: Main script enhanced_theme_generator.py not found
    echo ERROR: Main script enhanced_theme_generator.py not found >> %LOGFILE%
    goto :error
)

echo.
echo Step 1: Creating virtual environment...
echo Step 1: Creating virtual environment... >> %LOGFILE%

REM Create virtual env with output capture
python -m venv venv >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo ERROR: Failed to create virtual environment >> %LOGFILE%
    goto :error
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo ERROR: Failed to activate virtual environment >> %LOGFILE%
    goto :error
)

echo.
echo Step 2: Installing required packages...
echo Step 2: Installing required packages... >> %LOGFILE%

echo Upgrading pip, wheel, setuptools and build...
echo -----------------------------------------
venv\Scripts\python.exe -m pip install -U pip wheel setuptools build >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to update base packages
    echo ERROR: Failed to update base packages >> %LOGFILE%
    goto :error
)

echo Installing PyQt6, numpy, pillow, and pyinstaller...
echo -----------------------------------------
venv\Scripts\python.exe -m pip install PyQt6 numpy pillow pyinstaller >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages
    echo ERROR: Failed to install required packages >> %LOGFILE%
    goto :error
)

echo Checking if all packages are installed properly:
venv\Scripts\python.exe -m pip list >> %LOGFILE% 2>&1
echo -----------------------------------------

echo.
echo Step 3: Checking for icon creation script...
echo Step 3: Checking for icon creation script... >> %LOGFILE%

if exist "create_icon_script.py" (
    echo Creating app icon...
    venv\Scripts\python.exe create_icon_script.py >> %LOGFILE% 2>&1
    if %errorlevel% neq 0 (
        echo WARNING: Icon creation failed, continuing with default icon
        echo WARNING: Icon creation failed, continuing with default icon >> %LOGFILE%
    )
) else (
    echo WARNING: Icon creation script not found, continuing with default icon
    echo WARNING: Icon creation script not found, continuing with default icon >> %LOGFILE%
)

echo.
echo Step 4: Building Python package...
echo Step 4: Building Python package... >> %LOGFILE%
venv\Scripts\python.exe -m build >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Python package
    echo ERROR: Failed to build Python package >> %LOGFILE%
    goto :error
)

echo.
echo Step 5: Checking PyInstaller spec file...
echo Step 5: Checking PyInstaller spec file... >> %LOGFILE%
if not exist "pyinstaller.spec" (
    echo ERROR: PyInstaller spec file not found
    echo ERROR: PyInstaller spec file not found >> %LOGFILE%
    goto :error
)

echo.
echo Step 6: Creating executable with PyInstaller...
echo Step 6: Creating executable with PyInstaller... >> %LOGFILE%
venv\Scripts\python.exe -m PyInstaller --log-level DEBUG pyinstaller.spec >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller failed to create executable
    echo ERROR: PyInstaller failed to create executable >> %LOGFILE%
    goto :error
)

echo.
echo Checking if executable was created...
echo Checking if executable was created... >> %LOGFILE%
if not exist "dist\EnhancedThemeStudio.exe" (
    echo ERROR: Executable not found after PyInstaller completed
    echo ERROR: Executable not found after PyInstaller completed >> %LOGFILE%
    goto :error
)

echo.
echo ========================================
echo Packaging complete!
echo.
echo Python package available in: dist/
echo Executable available in: dist/EnhancedThemeStudio.exe
echo.
echo To install the package locally:
echo venv\Scripts\python.exe -m pip install -e .
echo.
echo To run the executable:
echo dist\EnhancedThemeStudio.exe
echo ========================================
echo.
echo Full log available in: %LOGFILE%

call venv\Scripts\deactivate.bat
goto :end

:error
echo.
echo An error occurred during packaging.
echo Please check the log file %LOGFILE% for detailed information.
echo.

:end
echo.
echo Press any key to exit...
pause 