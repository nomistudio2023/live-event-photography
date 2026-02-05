#!/bin/bash
# Build script for Live Event Photography Mac App

set -e

echo "================================================"
echo "🔧 Building Live Event Photo Mac App"
echo "================================================"

# Change to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/

# Build the app
echo "🔨 Building Mac App with PyInstaller..."
pyinstaller LiveEventPhoto.spec --clean

# Check if build succeeded
if [ -d "dist/Live Event Photo.app" ]; then
    echo ""
    echo "================================================"
    echo "✅ Build successful!"
    echo "================================================"
    echo ""
    echo "📁 App location: dist/Live Event Photo.app"
    echo ""
    echo "To install:"
    echo "  1. Drag 'Live Event Photo.app' to Applications folder"
    echo "  2. Or run directly from dist/ folder"
    echo ""
    echo "⚠️  Note: On first launch, you may need to:"
    echo "     Right-click → Open → Open"
    echo "     (to bypass Gatekeeper for unsigned app)"
    echo ""

    # Open the dist folder
    open dist/
else
    echo "❌ Build failed!"
    exit 1
fi
