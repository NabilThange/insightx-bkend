@echo off
echo Starting InsightX Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your Supabase credentials.
    pause
    exit /b 1
)

echo Starting server...
echo Server will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
uvicorn main:app --reload
