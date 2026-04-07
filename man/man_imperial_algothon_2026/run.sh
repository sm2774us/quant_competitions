#!/usr/bin/env bash
# =============================================================================
# run.sh — Algothon 2026 Strategy Engine entry point (Linux / macOS)
#
# Usage:
#   ./run.sh [local|docker] [backtest|submit] [OPTIONS]
#
# Examples:
#   ./run.sh local backtest --team myteam --round 1
#   ./run.sh local submit   --team myteam --round 2
#   ./run.sh docker backtest
#   ./run.sh docker jupyter
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# ── Colour helpers ─────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }

# ── Defaults ──────────────────────────────────────────────────────────────
MODE="${1:-local}"
ACTION="${2:-backtest}"
TEAM="${TEAM_NAME:-algothon_team}"
ROUND="${ROUND_NUMBER:-1}"
DATA_DIR="data/sample"
OUTPUT_DIR="submissions"
RISK_AVERSION="${RISK_AVERSION:-2.0}"
BLEND_ALPHA="${BLEND_ALPHA:-0.7}"

# ── Prerequisite checks ────────────────────────────────────────────────────
check_prerequisite() {
    command -v "$1" &>/dev/null || error "$1 is required but not installed."
}

# ── Build C++ extension ────────────────────────────────────────────────────
build_cpp() {
    #info "Building C++ portfolio engine..."
    #CMAKE_BIN=$(command -v cmake3 2>/dev/null || command -v cmake)
    #${CMAKE_BIN} -S . -B build_cpp \
    #    -DCMAKE_BUILD_TYPE=Release \
    #    -GNinja 2>/dev/null || \
    #${CMAKE_BIN} -S . -B build_cpp -DCMAKE_BUILD_TYPE=Release
    #${CMAKE_BIN} --build build_cpp --parallel "$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)"
    #${CMAKE_BIN} --install build_cpp
    #success "C++ extension built and installed."

    info "Building C++ portfolio engine..."

    # 1. Identify which binary to use
    local cmake_cmd
    cmake_cmd=$(command -v cmake3 || command -v cmake)

    # 2. Use your existing check_prerequisite to validate/fail
    check_prerequisite "${cmake_cmd:-cmake}"

    # 3. Detect cores for parallel build
    local cores
    cores=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

    # 4. Configure: Try Ninja first, fallback to default
    if ! "$cmake_cmd" -S . -B build_cpp -DCMAKE_BUILD_TYPE=Release -GNinja 2>/dev/null; then
        warn "Ninja not found or failed, falling back to default generator..."
        "$cmake_cmd" -S . -B build_cpp -DCMAKE_BUILD_TYPE=Release || {
            error "CMake configuration failed."
            return 1
        }
    fi

    # 5. Build and Install (with explicit failure handling)
    "$cmake_cmd" --build build_cpp --parallel "$cores" || { error "Build failed."; return 1; }
    "$cmake_cmd" --install build_cpp || { error "Install failed."; return 1; }

    success "C++ extension built and installed."
}

# ── Install Python dependencies ────────────────────────────────────────────
install_python() {
    info "Installing Python dependencies via Poetry..."
    check_prerequisite poetry
    poetry install --only main
    success "Python dependencies installed."
}

# ── Local mode ─────────────────────────────────────────────────────────────
run_local() {
    check_prerequisite python3

    # Check Python version
    PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [[ "$PY_MAJOR" -lt 3 || ("$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 13) ]]; then
        warn "Python 3.13+ recommended (found $PY_VER). Proceeding anyway..."
    fi

    # Build C++ if not already built
    if [[ ! -f "src/python/algothon_cpp"*.so ]] && \
       [[ ! -f "src/python/algothon_cpp"*.pyd ]]; then
        if command -v cmake &>/dev/null; then
            build_cpp
        else
            warn "cmake not found; C++ extension not built. Python fallback will be used."
        fi
    fi

    install_python

    mkdir -p "$OUTPUT_DIR"

    case "$ACTION" in
        backtest)
            info "Running backtest (team=$TEAM, round=$ROUND)..."
            poetry run python -m src.python.execution.engine \
                --data-dir "$DATA_DIR" \
                --team "$TEAM" \
                --round "$ROUND" \
                --risk-aversion "$RISK_AVERSION" \
                --blend-alpha "$BLEND_ALPHA" \
                --backtest \
                --output-dir "$OUTPUT_DIR" \
                "${@:3}"
            ;;
        submit)
            info "Generating submission (team=$TEAM, round=$ROUND)..."
            poetry run python -m src.python.execution.engine \
                --data-dir "$DATA_DIR" \
                --team "$TEAM" \
                --round "$ROUND" \
                --output-dir "$OUTPUT_DIR" \
                "${@:3}"
            ;;
        test)
            info "Running test suite..."
            poetry run pytest tests/python/ -v --tb=short
            ;;
        jupyter)
            info "Launching JupyterLab..."
            poetry run jupyter lab --notebook-dir=notebooks --no-browser
            ;;
        *)
            error "Unknown action: $ACTION. Use: backtest|submit|test|jupyter"
            ;;
    esac
}

# ── Docker mode ────────────────────────────────────────────────────────────
run_docker() {
    check_prerequisite docker

    case "$ACTION" in
        backtest|submit)
            info "Building Docker image..."
            docker compose build algothon
            info "Running in Docker (team=$TEAM, round=$ROUND, action=$ACTION)..."
            TEAM_NAME="$TEAM" ROUND_NUMBER="$ROUND" \
            RISK_AVERSION="$RISK_AVERSION" BLEND_ALPHA="$BLEND_ALPHA" \
            docker compose run --rm algothon \
                --data-dir /app/data/sample \
                --team "$TEAM" \
                --round "$ROUND" \
                $( [[ "$ACTION" == "backtest" ]] && echo "--backtest" )
            ;;
        jupyter)
            info "Starting JupyterLab in Docker on http://localhost:8888 ..."
            docker compose up jupyter
            ;;
        down)
            docker compose down --remove-orphans
            ;;
        *)
            error "Unknown docker action: $ACTION"
            ;;
    esac
}

# ── Dispatch ──────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}══════════════════════════════════════════════"
echo -e " Algothon 2026 — Man Group × Imperial College"
echo -e "══════════════════════════════════════════════${RESET}"
echo ""
info "Mode: $MODE | Action: $ACTION | Team: $TEAM | Round: $ROUND"
echo ""

case "$MODE" in
    local)  run_local  "$@" ;;
    docker) run_docker "$@" ;;
    *)      error "Unknown mode: $MODE. Use: local|docker" ;;
esac

success "Done."
