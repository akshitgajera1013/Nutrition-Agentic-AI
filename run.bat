@echo off
setlocal enabledelayedexpansion
:: ============================================================
::  NutriGuide Agentic AI — Windows Launcher
::  IBM Granite LLM · Watsonx.ai · Flask Web App
:: ============================================================
title NutriGuide Agentic AI Launcher

color 0B
echo.
echo  =========================================================
echo   NutriGuide - Nutrition Agentic AI
echo   Powered by IBM Granite 3.3 (Watsonx.ai)
echo  =========================================================
echo.

:: ---- Step 1: Check Python ----
echo [1/5] Checking Python installation...
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo.
    echo  ERROR: Python not found!
    echo  Please install Python 3.9+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo  Found: %%v
echo.

:: ---- Step 2: Setup .env ----
echo [2/5] Checking environment configuration...
IF NOT EXIST ".env" (
    IF EXIST ".env.example" (
        copy ".env.example" ".env" >nul
        echo  Created .env from template.
    )
)

IF EXIST ".env" (
    :: Check if API key is still the placeholder
    findstr /C:"your_ibm_watsonx_api_key_here" ".env" >nul 2>&1
    IF NOT ERRORLEVEL 1 (
        echo.
        echo  =========================================================
        echo   IBM Watsonx.ai Configuration (Optional)
        echo  =========================================================
        echo   To use IBM Granite AI, enter your credentials below.
        echo   Press ENTER to skip and run in Demo Mode.
        echo  =========================================================
        echo.
        set /p APIKEY="  Watsonx API Key (leave blank for Demo Mode): "
        if NOT "!APIKEY!"=="" (
            set /p PROJID="  Watsonx Project ID: "
            :: Update .env using PowerShell for reliability
            powershell -Command "(Get-Content .env) -replace 'your_ibm_watsonx_api_key_here', '!APIKEY!' | Set-Content .env"
            IF NOT "!PROJID!"=="" (
                powershell -Command "(Get-Content .env) -replace 'your_watsonx_project_id_here', '!PROJID!' | Set-Content .env"
            )
            echo  API credentials saved to .env
        ) else (
            echo  Skipped — running in Demo Mode.
        )
    ) else (
        echo  API key already configured.
    )
) else (
    echo  No .env file found — running in Demo Mode.
)
echo.

:: ---- Step 3: Virtual Environment ----
echo [3/5] Setting up Python virtual environment...
IF NOT EXIST "venv\" (
    echo  Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
) else (
    echo  Virtual environment already exists.
)
echo.

:: ---- Step 4: Install Dependencies ----
echo [4/5] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
IF ERRORLEVEL 1 (
    echo.
    echo  ERROR: Failed to install dependencies.
    echo  Try running: pip install -r requirements.txt manually.
    pause
    exit /b 1
)
echo  All dependencies installed successfully.
echo.

:: ---- Step 5: Create plans directory ----
IF NOT EXIST "plans\" (
    mkdir plans
    echo  Created plans\ directory for saving nutrition plans.
)

:: ---- Launch ----
echo [5/5] Starting NutriGuide Agentic AI...
echo.
echo  =========================================================
echo   Application is starting...
echo   Open your browser at: http://localhost:5000
echo   Press Ctrl+C to stop the server
echo  =========================================================
echo.

:: Small delay then open browser
start "" /b timeout /t 2 /nobreak >nul
start http://localhost:5000

:: Run Flask app
python app.py

echo.
echo  NutriGuide has stopped.
pause
