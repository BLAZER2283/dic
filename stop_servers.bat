@echo off
echo ========================================
echo      DIC Analyzer - Stop Servers
echo ========================================
echo.

echo Stopping Python processes...
taskkill /f /im python.exe /t 2>nul
taskkill /f /im python3.exe /t 2>nul

echo.
echo Stopping Node.js processes (if any)...
taskkill /f /im node.exe /t 2>nul
taskkill /f /im npm.cmd /t 2>nul

echo.
echo Stopping Java processes (if any)...
taskkill /f /im java.exe /t 2>nul

echo.
echo ========================================
echo         Servers Stopped!
echo ========================================
echo.
pause
