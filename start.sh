#!/bin/bash

# Canvas App Backend - Start Script
# Uses venv directly without requiring shell activation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PID_FILE="$SCRIPT_DIR/.uvicorn.pid"
LOG_FILE="$SCRIPT_DIR/uvicorn.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Start uvicorn using venv's Python directly
echo "Starting Canvas App Backend..."
cd "$SCRIPT_DIR"

nohup "$VENV_DIR/bin/uvicorn" app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    > "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$PID_FILE"
sleep 2

# Check if started successfully
if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
    echo -e "${GREEN}Backend started successfully (PID: $(cat $PID_FILE))${NC}"
    echo ""
    echo "  API:     http://localhost:8000"
    echo "  Docs:    http://localhost:8000/docs"
    echo "  ReDoc:   http://localhost:8000/redoc"
    echo "  Logs:    $LOG_FILE"
    echo ""
    echo "Use ./stop.sh to stop the server"
else
    echo -e "${RED}Failed to start backend${NC}"
    echo "Check logs: tail -50 $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
