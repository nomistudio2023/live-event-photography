#!/bin/bash
# Simple launcher for Live Event Photography
# Double-click this file to start the server and open the admin panel

cd "$(dirname "$0")"

echo "================================================"
echo "📸 Live Event Photography - Starting..."
echo "================================================"
echo ""

# Check if script exists
LAUNCH_SCRIPT="./scripts/start_event.sh"

if [ -f "$LAUNCH_SCRIPT" ]; then
    bash "$LAUNCH_SCRIPT"
else
    echo "❌ Error: Cannot find launch script at $LAUNCH_SCRIPT"
    echo "Current directory: $(pwd)"
    read -p "Press Enter to exit..."
    exit 1
fi
