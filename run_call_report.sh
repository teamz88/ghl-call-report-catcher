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

# Preflight: ensure Python deps are available; auto-install if missing
echo "Preflight: checking Python dependencies" >> "$LOG_FILE"
"$PYTHON_BIN" -c "import msal, requests, playwright, dotenv" >/dev/null 2>&1 || {
  echo "Installing Python dependencies..." >> "$LOG_FILE"
  "$PYTHON_BIN" -m pip install --user -r "$PROJECT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1
}

# Install Playwright browsers once (idempotent with marker file)
if [ ! -f "$PROJECT_DIR/.playwright_installed" ]; then
  echo "Installing Playwright browsers..." >> "$LOG_FILE"
  "$PYTHON_BIN" -m playwright install >> "$LOG_FILE" 2>&1 && touch "$PROJECT_DIR/.playwright_installed"
fi

cd "$PROJECT_DIR"

echo "Starting login_automation at $(date)" >> "$LOG_FILE"
set +e
"$PYTHON_BIN" "$PROJECT_DIR/login_automation.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
set -e

echo "Finished with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
exit "$EXIT_CODE"