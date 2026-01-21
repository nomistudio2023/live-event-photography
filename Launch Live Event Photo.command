#!/bin/bash
# Simple launcher for Live Event Photography
# Double-click this file to start the server and open the admin panel

cd "$(dirname "$0")"

echo "================================================"
echo "📸 Live Event Photography - Starting..."
echo "================================================"
echo ""

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use!"
    echo "   Opening existing server..."
    open "http://localhost:8000"
    exit 0
fi

# Start the server in background
echo "🚀 Starting server on http://localhost:8000"
python3 server.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started (PID: $SERVER_PID)"
    echo ""
    echo "📱 Opening Admin Panel..."
    open "http://localhost:8000"
    echo ""
    echo "================================================"
    echo "Server is running. Close this window to stop."
    echo "================================================"
    echo ""
    echo "Press Ctrl+C to stop the server..."

    # Wait for the server process
    wait $SERVER_PID
else
    echo "❌ Server failed to start!"
    exit 1
fi
