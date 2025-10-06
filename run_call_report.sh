#!/usr/bin/env bash
set -euo pipefail

# Cron-friendly runner for Call Report Catcher
# - Loads environment variables from .env
# - Writes logs per run to logs/ directory
# - Prevents overlapping runs with a lock file

# Configure PATH for cron (cron has a minimal environment)
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

PROJECT_DIR="/Users/bro/PROJECTS/callreportcatcher"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/run_$TIMESTAMP.log"
LOCK_DIR="$PROJECT_DIR/.cron_lock_dir"

mkdir -p "$LOG_DIR"

# Acquire lock to avoid concurrent runs (portable, without flock)
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another run is in progress; exiting." >> "$LOG_FILE"
  exit 0
fi
cleanup() {
  rm -rf "$LOCK_DIR"
}
trap cleanup EXIT INT TERM

# Load environment variables from .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  . "$PROJECT_DIR/.env"
  set +a
fi

# Ensure python3 is available
PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$PYTHON_BIN" ]; then
  echo "python3 not found in PATH" >> "$LOG_FILE"
  exit 1
fi

# Use project-local virtual environment to avoid system package restrictions (PEP 668)
VENV_DIR="$PROJECT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..." >> "$LOG_FILE"
  "$PYTHON_BIN" -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
fi

echo "Ensuring Python dependencies in venv..." >> "$LOG_FILE"
"$PIP_BIN" install --upgrade pip wheel setuptools >> "$LOG_FILE" 2>&1
"$PIP_BIN" install -r "$PROJECT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1

# Install Playwright browsers once per venv
if [ ! -f "$VENV_DIR/.playwright_installed" ]; then
  echo "Installing Playwright browsers (venv)..." >> "$LOG_FILE"
  "$VENV_PY" -m playwright install >> "$LOG_FILE" 2>&1 && touch "$VENV_DIR/.playwright_installed"
fi

cd "$PROJECT_DIR"

echo "Starting login_automation at $(date)" >> "$LOG_FILE"
set +e
"$VENV_PY" "$PROJECT_DIR/login_automation.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
set -e

echo "Finished with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
exit "$EXIT_CODE"