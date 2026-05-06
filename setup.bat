@echo off
REM Resume Parser Setup Script for Windows
REM Run this script to quickly set up the project

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════╗
echo ║  Resume Parser - Quick Setup           ║
echo ╚════════════════════════════════════════╝
echo.

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Create virtual environment
echo.
echo 🔧 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📚 Installing dependencies...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Create necessary directories
echo.
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates
echo ✅ Directories created

REM Check configuration files
echo.
echo 🔐 Checking configuration...

if not exist ".env" (
    echo ⚠️  .env file not found
    (
        echo # Environment Variables
        echo # Add your OpenRouter API key here
        echo OPENROUTER_API_KEY=your_api_key_here
    ) > .env
    echo    Created .env template
)

if not exist "config.yaml" (
    echo ⚠️  config.yaml not found
    (
        echo # Resume Parser Configuration
        echo OPENROUTER_API_KEY: "your_api_key_here"
    ) > config.yaml
    echo    Created config.yaml template
)

REM Summary
echo.
echo ╔════════════════════════════════════════╗
echo ║  ✅ Setup Complete!                    ║
echo ╚════════════════════════════════════════╝
echo.
echo 📝 Next Steps:
echo.
echo 1. Configure your API key:
echo    - Get free key at: https://openrouter.ai/keys
echo    - Edit .env or config.yaml
echo.
echo 2. Run the application:
echo    python app.py
echo.
echo 3. Open your browser:
echo    http://localhost:8000
echo.
echo 4. (Optional) Run tests:
echo    python test_openrouter.py
echo.
echo 📚 Documentation: See README.md for more information
echo.
pause
