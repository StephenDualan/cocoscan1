@echo off
echo ========================================
echo    CocoScan Mobile App Builder Setup
echo ========================================
echo.
echo This script will install WSL (Windows Subsystem for Linux)
echo which is required to build Android APKs on Windows.
echo.
echo Press any key to continue...
pause >nul

echo.
echo Installing WSL...
wsl --install

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Please restart your computer, then:
echo 1. Open WSL terminal
echo 2. Navigate to your project: cd /mnt/c/Users/steph/OneDrive/Desktop/cocoscan
echo 3. Run: buildozer android debug
echo.
echo For detailed instructions, see README_MOBILE.md
echo.
pause 