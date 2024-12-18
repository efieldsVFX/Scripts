@echo off
echo Starting Social Media Analytics Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if it doesn't
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please make sure you have venv installed.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip to latest version
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install wheel and setuptools first
echo Installing base dependencies...
pip install wheel setuptools

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies. Please check your internet connection and try again.
    pause
    exit /b 1
)

REM Download spaCy model
echo Downloading spaCy model...
python -m spacy download en_core_web_sm

REM Start the server in the background
echo Starting the server...
cd src
start /B python server.py

REM Wait a few seconds for the server to start
timeout /t 5 /nobreak

REM Start the dashboard
echo Starting the dashboard...
streamlit run dashboard.py

REM Deactivate virtual environment when done
deactivate
