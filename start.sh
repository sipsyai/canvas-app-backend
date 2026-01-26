#!/bin/bash

# Canvas App Backend - Start Script
# Uses venv directly without requiring shell activation
# Log rotation: 1MB max, ISO 8601 timestamps

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PID_FILE="$SCRIPT_DIR/.uvicorn.pid"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_PREFIX="canvas-backend"
MAX_LOG_SIZE=1048576  # 1MB in bytes

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$LOG_DIR"

# Log rotation function - runs as background process
log_rotator() {
    local current_log="$LOG_DIR/${LOG_PREFIX}-$(date -u +%Y-%m-%dT%H-%M-%SZ).log"
    local current_size=0

    # Write startup marker
    echo "[$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)] [INFO] [system] Log started - Canvas App Backend" >> "$current_log"

    while IFS= read -r line; do
        # Add ISO 8601 timestamp if line doesn't have one
        if [[ ! "$line" =~ ^\[20[0-9]{2}- ]]; then
            line="[$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)] $line"
        fi

        # Write line to current log
        echo "$line" >> "$current_log"

        # Check file size
        if [ -f "$current_log" ]; then
            current_size=$(stat -f%z "$current_log" 2>/dev/null || stat -c%s "$current_log" 2>/dev/null || echo 0)
        fi

        # Rotate if exceeds max size
        if [ "$current_size" -ge "$MAX_LOG_SIZE" ]; then
            echo "[$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)] [INFO] [system] Log rotated - size limit reached (1MB)" >> "$current_log"
            current_log="$LOG_DIR/${LOG_PREFIX}-$(date -u +%Y-%m-%dT%H-%M-%SZ).log"
            current_size=0
            echo "[$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)] [INFO] [system] New log file created" >> "$current_log"
        fi
    done
}

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Check if uvicorn is installed in venv
if [ ! -f "$VENV_DIR/bin/uvicorn" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}Dependencies installed${NC}"
fi

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Backend already running (PID: $PID)${NC}"
        echo "Use ./stop.sh to stop it first"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Clean up old logs (keep last 10)
echo -e "${CYAN}Cleaning old logs (keeping last 10)...${NC}"
ls -t "$LOG_DIR"/${LOG_PREFIX}-*.log 2>/dev/null | tail -n +11 | xargs -r rm -f

# Start uvicorn using venv's Python directly with log rotation
echo "Starting Canvas App Backend..."
cd "$SCRIPT_DIR"

# Start uvicorn and pipe to log rotator
"$VENV_DIR/bin/uvicorn" app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    2>&1 | log_rotator &

# Save PID of the uvicorn process (not the pipe)
UVICORN_PID=$!
echo $UVICORN_PID > "$PID_FILE"
sleep 2

# Get current log file
CURRENT_LOG=$(ls -t "$LOG_DIR"/${LOG_PREFIX}-*.log 2>/dev/null | head -1)

# Check if started successfully
if ps -p "$UVICORN_PID" > /dev/null 2>&1; then
    echo -e "${GREEN}Backend started successfully (PID: $UVICORN_PID)${NC}"
    echo ""
    echo "  API:     http://localhost:8000"
    echo "  Docs:    http://localhost:8000/docs"
    echo "  ReDoc:   http://localhost:8000/redoc"
    echo ""
    echo -e "${CYAN}Log Settings:${NC}"
    echo "  Directory:    $LOG_DIR"
    echo "  Current Log:  $CURRENT_LOG"
    echo "  Max Size:     1MB (auto-rotation)"
    echo "  Format:       ISO 8601 UTC timestamps"
    echo "  Retention:    Last 10 files"
    echo ""
    echo "  View logs:    tail -f $LOG_DIR/${LOG_PREFIX}-*.log"
    echo ""
    echo "Use ./stop.sh to stop the server"
else
    echo -e "${RED}Failed to start backend${NC}"
    if [ -n "$CURRENT_LOG" ]; then
        echo "Check logs: tail -50 $CURRENT_LOG"
    fi
    rm -f "$PID_FILE"
    exit 1
fi
