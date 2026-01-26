#!/bin/bash

# Canvas App Backend - Stop Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.uvicorn.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}Backend is not running (no PID file found)${NC}"

    # Check if uvicorn is running anyway
    UVICORN_PID=$(pgrep -f "uvicorn app.main:app")
    if [ -n "$UVICORN_PID" ]; then
        echo -e "${YELLOW}Found orphan uvicorn process (PID: $UVICORN_PID)${NC}"
        read -p "Kill it? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $UVICORN_PID 2>/dev/null
            sleep 1
            # Kill child processes too
            pkill -f "uvicorn app.main:app" 2>/dev/null
            echo -e "${GREEN}Killed orphan process${NC}"
        fi
    fi
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "Stopping backend (PID: $PID)..."
    kill "$PID" 2>/dev/null

    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 0.5
    done

    # Force kill if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Force killing...${NC}"
        kill -9 "$PID" 2>/dev/null
    fi

    # Also kill any child uvicorn processes
    pkill -f "uvicorn app.main:app" 2>/dev/null

    echo -e "${GREEN}Backend stopped${NC}"
else
    echo -e "${YELLOW}Backend was not running (stale PID file)${NC}"
fi

rm -f "$PID_FILE"
