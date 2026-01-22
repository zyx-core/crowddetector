@echo off
echo ========================================
echo   CPU-Only Build (Smallest Size)
echo ========================================
echo.
echo This build removes CUDA support for
echo minimum file size (~200MB)
echo.
echo WARNING: GPU acceleration disabled!
echo Performance will be slower.
echo.
pause

REM Uninstall GPU packages
echo [0/3] Removing GPU packages...
pip uninstall -y tensorflow tensorflow-intel keras tensorboard 2>nul

echo [1/3] Cleaning...
if exist "dist\CrowdSense.exe" del "dist\CrowdSense.exe"
if exist "build" rmdir /s /q "build"

echo [2/3] Building CPU-only executable...
pyinstaller crowdsense_cpu.spec --clean

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [3/3] Done!
for %%A in ("dist\CrowdSense.exe") do set /a sizeMB=%%~zA/1048576

echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo.
echo Output: dist\CrowdSense.exe
echo Size: %sizeMB% MB (CPU-only)
echo.
pause
