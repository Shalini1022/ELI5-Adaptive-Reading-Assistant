@echo off
setlocal
cd /d "%~dp0"
echo Creating virtual environment...
if not exist venv python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Installation failed. Check the error above.
  pause
  exit /b 1
)
echo.
echo Starting ELI5 Adaptive Reading Assistant...
python -m streamlit run app.py
pause
