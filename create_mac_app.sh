#!/bin/bash
# Create a simple Mac .app bundle using osacompile
# This creates a native Mac application without additional dependencies

set -e

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

APP_NAME="Live Event Photo"
APP_PATH="${PROJECT_DIR}/dist/${APP_NAME}.app"

echo "================================================"
echo "🔧 Creating Mac App: ${APP_NAME}"
echo "================================================"

# Create dist directory
mkdir -p dist

# Create the AppleScript
SCRIPT_CONTENT="
-- Live Event Photo Launcher
-- Auto-generated AppleScript

on run
    set projectPath to \"${PROJECT_DIR}\"
    set serverScript to projectPath & \"/server.py\"

    -- Check if server is already running
    try
        do shell script \"lsof -i :8000 | grep LISTEN\"
        -- Server already running, just open browser
        tell application \"System Events\"
            open location \"http://localhost:8000\"
        end tell
        display notification \"Opening existing server...\" with title \"Live Event Photo\"
        return
    end try

    -- Start server in Terminal
    tell application \"Terminal\"
        activate
        set serverWindow to do script \"cd '\" & projectPath & \"' && python3 server.py\"
        set custom title of front window to \"Live Event Photo Server\"
    end tell

    -- Wait for server to start
    delay 2

    -- Open browser
    tell application \"System Events\"
        open location \"http://localhost:8000\"
    end tell

    display notification \"Server started on http://localhost:8000\" with title \"Live Event Photo\" subtitle \"Admin Panel Opening...\"
end run
"

# Create temporary AppleScript file
TEMP_SCRIPT="/tmp/LiveEventPhoto.applescript"
echo "$SCRIPT_CONTENT" > "$TEMP_SCRIPT"

# Compile to .app
echo "📦 Compiling AppleScript to app bundle..."
osacompile -o "$APP_PATH" "$TEMP_SCRIPT"

# Clean up temp file
rm "$TEMP_SCRIPT"

# Create Info.plist additions
INFO_PLIST="${APP_PATH}/Contents/Info.plist"
if [ -f "$INFO_PLIST" ]; then
    # Add custom properties using PlistBuddy
    /usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string com.liveevent.photo" "$INFO_PLIST" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Add :CFBundleVersion string 2.3.0" "$INFO_PLIST" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string 2.3" "$INFO_PLIST" 2>/dev/null || true
fi

echo ""
echo "================================================"
echo "✅ Mac App created successfully!"
echo "================================================"
echo ""
echo "📁 App location: ${APP_PATH}"
echo ""
echo "To install:"
echo "  • Drag '${APP_NAME}.app' to your Applications folder"
echo "  • Or double-click to run from current location"
echo ""
echo "First launch note:"
echo "  If macOS blocks the app, right-click → Open → Open"
echo ""

# Open the dist folder
open dist/
