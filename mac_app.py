#!/usr/bin/env python3
"""
Live Event Photography - Mac Menu Bar App
Provides a menu bar interface to control the server.
"""

import os
import sys
import threading
import webbrowser
import subprocess
import signal
from pathlib import Path

# Determine the base path (for PyInstaller bundled app)
if getattr(sys, 'frozen', False):
    # Running as bundled app
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(os.path.dirname(sys.executable)).parent.parent.parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    APP_DIR = BASE_DIR

# Add base dir to path for imports
sys.path.insert(0, str(BASE_DIR))

import rumps
import uvicorn
from server import app as fastapi_app, CONFIG

class LiveEventApp(rumps.App):
    def __init__(self):
        super().__init__(
            "📸",
            title="📸",
            quit_button=None  # We'll add custom quit
        )

        self.server_thread = None
        self.server_running = False

        # Menu items
        self.menu = [
            rumps.MenuItem("🟢 Server Running", callback=None),
            None,  # Separator
            rumps.MenuItem("Open Admin Panel", callback=self.open_admin),
            rumps.MenuItem("Open Live Gallery", callback=self.open_gallery),
            None,  # Separator
            rumps.MenuItem("Start Server", callback=self.start_server),
            rumps.MenuItem("Stop Server", callback=self.stop_server),
            None,  # Separator
            rumps.MenuItem("Open Project Folder", callback=self.open_folder),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        # Update working directory
        os.chdir(str(APP_DIR))

        # Auto-start server
        self.start_server(None)

    def update_status(self):
        """Update the menu bar status indicator"""
        if self.server_running:
            self.title = "📸"
            self.menu["🟢 Server Running"].title = "🟢 Server Running"
            self.menu["Start Server"].set_callback(None)
            self.menu["Stop Server"].set_callback(self.stop_server)
        else:
            self.title = "📷"
            self.menu["🟢 Server Running"].title = "🔴 Server Stopped"
            self.menu["Start Server"].set_callback(self.start_server)
            self.menu["Stop Server"].set_callback(None)

    def start_server(self, _):
        """Start the FastAPI server"""
        if self.server_running:
            return

        def run_server():
            try:
                uvicorn.run(
                    fastapi_app,
                    host="0.0.0.0",
                    port=8000,
                    log_level="warning"
                )
            except Exception as e:
                print(f"Server error: {e}")
                self.server_running = False
                self.update_status()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.server_running = True
        self.update_status()

        # Show notification
        rumps.notification(
            title="Live Event Photography",
            subtitle="Server Started",
            message="Admin panel: http://localhost:8000"
        )

        # Open browser after a short delay
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8000")).start()

    def stop_server(self, _):
        """Stop the server (note: uvicorn doesn't stop gracefully in thread)"""
        if not self.server_running:
            return

        # Since uvicorn in a thread can't be stopped gracefully,
        # we just mark it as stopped and the app will need to restart
        rumps.notification(
            title="Live Event Photography",
            subtitle="Note",
            message="To fully stop the server, please quit the app."
        )

    def open_admin(self, _):
        """Open the admin panel in browser"""
        webbrowser.open("http://localhost:8000")

    def open_gallery(self, _):
        """Open the live gallery in browser"""
        webbrowser.open("http://localhost:8000/gallery")

    def open_folder(self, _):
        """Open the project folder in Finder"""
        subprocess.run(["open", str(APP_DIR)])

    def quit_app(self, _):
        """Quit the application"""
        rumps.quit_application()


if __name__ == "__main__":
    LiveEventApp().run()
