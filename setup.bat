@echo off
REM Setup script for Diabetes Prediction System
echo =========================================
echo Diabetes Prediction System - Setup
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python packages
    pause
    exit /b 1
)

echo.
echo [2/4] Setting up frontend...
cd diabetes-frontend
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install Node packages
    pause
    exit /b 1
)

cd ..

echo.
echo [3/4] Checking for trained model...
if not exist "diabetes_model.pkl" (
    echo Warning: Model file not found. Run diabetes_predictor.py to train the model.
)

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To run the application:
echo.
echo Terminal 1 (Backend):
echo   uvicorn main:app --reload
echo.
echo Terminal 2 (Frontend):
echo   cd diabetes-frontend
echo   npm start
echo.
echo Then visit: http://localhost:3000
echo.
pause
