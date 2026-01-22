@echo off
echo ========================================
echo   Optimized Build - CrowdSense
echo ========================================
echo.
echo This build excludes TensorFlow and other
echo unnecessary packages to reduce size.
echo.
echo Expected size: ~300MB (vs 2.3GB)
echo.

REM Uninstall TensorFlow to prevent inclusion
echo [0/4] Removing TensorFlow (not needed)...
pip uninstall -y tensorflow tensorflow-intel keras tensorboard 2>nul

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found. Installing...
    pip install pyinstaller
)

echo [1/4] Cleaning previous builds...
if exist "dist\CrowdSense.exe" del "dist\CrowdSense.exe"
if exist "build" rmdir /s /q "build"

echo [2/4] Building optimized executable...
pyinstaller crowdsense.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo [3/4] Compressing with UPX...
echo (This may take a few minutes)

echo [4/4] Checking file size...
for %%A in ("dist\CrowdSense.exe") do (
    set size=%%~zA
    set /a sizeMB=%%~zA/1048576
)

echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo.
echo Output: dist\CrowdSense.exe
echo Size: %sizeMB% MB
echo.
if %sizeMB% GTR 500 (
    echo WARNING: File is larger than expected!
    echo Try running build_cpu_only.bat for smaller size
    echo.
)
echo To test: cd dist ^&^& CrowdSense.exe
echo.
echo NOTE: First launch may be slow (extracting files)
echo.
pause
