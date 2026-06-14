@echo off
echo ============================================
echo   Aura Store - Starting Development Server
echo ============================================
echo.

REM Activate the virtual environment
call "%~dp0.venv\Scripts\activate.bat"

echo [OK] Virtual environment activated
echo [OK] Starting Django server at http://127.0.0.1:8000/
echo.
echo Press CTRL+C to stop the server.
echo.

python manage.py runserver
pause
