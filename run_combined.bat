@echo off
REM Combined run script for Smart Tourism Analytics Platform
REM Runs both Flask backend and Streamlit frontend

echo.
echo ==========================================
echo Smart Tourism Analytics Platform Launcher
echo ==========================================
echo.
echo [1] Starting Flask API backend on port 5000...
start /B python app.py

REM Give Flask time to start
timeout /t 2 /nobreak

echo [OK] Flask API is running
echo.
echo [2] Starting Streamlit frontend...
echo ==========================================
echo.

REM Run Streamlit in the foreground
python -m streamlit run streamlit_app.py --client.showErrorDetails=true

echo.
echo [INFO] Application stopped
pause
