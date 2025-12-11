@echo off
echo ========================================
echo       DIC Analyzer - System Launcher
echo ========================================
echo.

echo [1/3] Activating Python virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [2/3] Starting Django backend server...
start "Django Backend - DIC Analyzer" cmd /k "cd app && python manage.py runserver 8000"

echo.
echo [3/3] Starting HTTP frontend server...
start "HTTP Frontend - DIC Analyzer" cmd /k "python -m http.server 8080"

echo.
echo ========================================
echo         DIC Analyzer Started!
echo ========================================
echo.
echo Django Backend: http://localhost:8000
echo Main Application: http://localhost:8080/working_app.html
echo API Documentation: http://localhost:8000/api/
echo Django Admin: http://localhost:8000/admin/
echo.
echo Press any key to close this launcher...
pause > nul
