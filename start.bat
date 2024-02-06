@echo off

setlocal enabledelayedexpansion
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed.
    exit /b
)

rem Get Python version string to check compatibility and find correct llamacpp wheel
for /f "delims=" %%V in ('python -V 2^>^&1') do (
    set "python_version=%%V"
)
for /f "tokens=2 delims=. " %%A in ("%python_version%") do (
    set "major_version=%%A"
)
for /f "tokens=3 delims=. " %%B in ("%python_version%") do (
    set "minor_version=%%B"
)
set "python_version_combined=%major_version%%minor_version%"
rem Check if the version is at least 3.10

if %python_version_combined% lss 310 (
    echo Python version is below 3.10. Please update.
    exit /b
)

REM Set the name of your virtual environment
set VENV_NAME=myvenv

REM Set the path where the virtual environment will be created
set VENV_PATH=%~dp0\%VENV_NAME%

REM Check if the virtual env folder exists
if not exist "%VENV_PATH%" (
    echo For first time use, creating virtual environment and installing dependencies. This will take some while.
    REM Create the virtual environment
    python -m venv %VENV_PATH%

    REM Activate the virtual environment
    call %VENV_PATH%\Scripts\activate.bat

    REM Install required packages using pip
    pip install -r requirements.txt
    set llama_win_wheel=https://github.com/abetlen/llama-cpp-python/releases/download/v0.2.28/llama_cpp_python-0.2.28-cp!python_version_combined!-cp!python_version_combined!-win_amd64.whl
    pip install !llama_win_wheel!

    echo Virtual environment "%VENV_NAME%" has been created, dependencies installed and activated.
    echo.
) else (
    REM Activate the virtual environment
    echo Activating the virtual environment.
    call %VENV_PATH%\Scripts\activate.bat
)
echo Starting application.
python app.py %*

REM Deactivate the virtual environment when finished
deactivate
