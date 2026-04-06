@echo off
REM =============================================================================
REM run.bat — Algothon 2026 Strategy Engine entry point (Windows 11)
REM
REM Usage:
REM   run.bat [local|docker] [backtest|submit|test|jupyter] [OPTIONS]
REM
REM Examples:
REM   run.bat local backtest --team myteam --round 1
REM   run.bat local submit   --team myteam --round 2
REM   run.bat docker backtest
REM   run.bat docker jupyter
REM =============================================================================

setlocal EnableDelayedExpansion

REM ── Default parameters ──────────────────────────────────────────────────
set MODE=%1
set ACTION=%2
if "%MODE%"=="" set MODE=local
if "%ACTION%"=="" set ACTION=backtest

if "%TEAM_NAME%"=="" set TEAM_NAME=algothon_team
if "%ROUND_NUMBER%"=="" set ROUND_NUMBER=1
if "%RISK_AVERSION%"=="" set RISK_AVERSION=2.0
if "%BLEND_ALPHA%"=="" set BLEND_ALPHA=0.7

set DATA_DIR=data\sample
set OUTPUT_DIR=submissions

echo.
echo ==============================================================
echo  Algothon 2026 -- Man Group x Imperial College
echo ==============================================================
echo Mode   : %MODE%
echo Action : %ACTION%
echo Team   : %TEAM_NAME%
echo Round  : %ROUND_NUMBER%
echo.

REM ── Check prerequisites ────────────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.13 from https://python.org
    exit /b 1
)

if "%MODE%"=="local" goto :local_mode
if "%MODE%"=="docker" goto :docker_mode
echo [ERROR] Unknown mode: %MODE%. Use local or docker.
exit /b 1

REM ── LOCAL MODE ──────────────────────────────────────────────────────────
:local_mode
where poetry >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Poetry...
    curl -sSL https://install.python-poetry.org | python -
    set PATH=%PATH%;%APPDATA%\Python\Scripts
)

echo [INFO] Installing Python dependencies...
call poetry install --only main
if errorlevel 1 (
    echo [ERROR] Poetry install failed.
    exit /b 1
)

REM Build C++ extension if cmake available
where cmake >nul 2>&1
if not errorlevel 1 (
    if not exist "src\python\algothon_cpp*.pyd" (
        echo [INFO] Building C++ portfolio engine...
        cmake -S . -B build_cpp -DCMAKE_BUILD_TYPE=Release -A x64
        cmake --build build_cpp --config Release --parallel
        cmake --install build_cpp
        if errorlevel 1 (
            echo [WARN] C++ build failed. Python-only fallback will be used.
        )
    )
) else (
    echo [WARN] cmake not found. C++ extension will not be built.
)

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

if "%ACTION%"=="backtest" goto :local_backtest
if "%ACTION%"=="submit"   goto :local_submit
if "%ACTION%"=="test"     goto :local_test
if "%ACTION%"=="jupyter"  goto :local_jupyter
echo [ERROR] Unknown action: %ACTION%
exit /b 1

:local_backtest
echo [INFO] Running backtest...
call poetry run python -m src.python.execution.engine ^
    --data-dir %DATA_DIR% ^
    --team %TEAM_NAME% ^
    --round %ROUND_NUMBER% ^
    --risk-aversion %RISK_AVERSION% ^
    --blend-alpha %BLEND_ALPHA% ^
    --backtest ^
    --output-dir %OUTPUT_DIR%
goto :end

:local_submit
echo [INFO] Generating submission...
call poetry run python -m src.python.execution.engine ^
    --data-dir %DATA_DIR% ^
    --team %TEAM_NAME% ^
    --round %ROUND_NUMBER% ^
    --output-dir %OUTPUT_DIR%
goto :end

:local_test
echo [INFO] Running Python test suite...
call poetry run pytest tests\python\ -v --tb=short
goto :end

:local_jupyter
echo [INFO] Launching JupyterLab at http://localhost:8888 ...
call poetry run jupyter lab --notebook-dir=notebooks --no-browser
goto :end

REM ── DOCKER MODE ─────────────────────────────────────────────────────────
:docker_mode
where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Install Docker Desktop from https://docker.com
    exit /b 1
)

if "%ACTION%"=="backtest" goto :docker_backtest
if "%ACTION%"=="submit"   goto :docker_submit
if "%ACTION%"=="jupyter"  goto :docker_jupyter
if "%ACTION%"=="down"     goto :docker_down
echo [ERROR] Unknown docker action: %ACTION%
exit /b 1

:docker_backtest
echo [INFO] Building and running Docker container...
docker compose build algothon
set TEAM_NAME=%TEAM_NAME%
set ROUND_NUMBER=%ROUND_NUMBER%
docker compose run --rm algothon ^
    --data-dir /app/data/sample ^
    --team %TEAM_NAME% ^
    --round %ROUND_NUMBER% ^
    --backtest
goto :end

:docker_submit
docker compose build algothon
docker compose run --rm algothon ^
    --data-dir /app/data/sample ^
    --team %TEAM_NAME% ^
    --round %ROUND_NUMBER%
goto :end

:docker_jupyter
echo [INFO] Starting JupyterLab in Docker on http://localhost:8888 ...
docker compose up jupyter
goto :end

:docker_down
docker compose down --remove-orphans
goto :end

:end
echo.
echo [OK] Done.
endlocal
