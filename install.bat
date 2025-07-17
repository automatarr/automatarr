@echo off
echo Installing Automatarr dependencies...
echo.

REM Check if UV is already installed
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo UV is already installed.
    goto install_deps
)

echo UV not found. Installing UV...
echo.

REM Install UV using the official installer
powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
if %errorlevel% neq 0 (
    echo Failed to install UV. Please install UV manually from https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Add UV to PATH for current session
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

echo UV installed successfully.
echo.

:install_deps
echo Installing project dependencies in editable mode with dev dependencies...
echo.

REM Install the project in editable mode with dev dependencies
uv add --dev --editable .
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo You can now run Automatarr using:
echo   uv run automatarr --help
echo.
pause
