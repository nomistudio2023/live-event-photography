-- Live Event Photo Launcher
-- Starts both server.py and sync_to_r2.py

on run
	set projectPath to "/Users/nomisas/.gemini/antigravity/scratch/live-event-photography"
	set serverScript to projectPath & "/server.py"
	set syncScript to projectPath & "/sync_to_r2.py"

	-- Check if server is already running
	set serverRunning to false
	try
		do shell script "lsof -i :8000 | grep LISTEN"
		set serverRunning to true
	end try

	if serverRunning then
		-- Server already running, just open browser
		tell application "System Events"
			open location "http://localhost:8000"
		end tell
		display notification "Opening existing server..." with title "Live Event Photo"
		return
	end if

	-- Start server in Terminal (Tab 1)
	tell application "Terminal"
		activate
		-- Create new window for server
		set serverWindow to do script "cd '" & projectPath & "' && python3 server.py"
		set custom title of front window to "Live Event Photo - Server"

		-- Wait a moment then create new tab for sync
		delay 0.5

		-- Create new tab for sync script
		tell application "System Events"
			keystroke "t" using command down
		end tell
		delay 0.3
		do script "cd '" & projectPath & "' && python3 sync_to_r2.py" in front window

		-- Rename tab
		delay 0.2
		set custom title of front window to "Live Event Photo - Sync"
	end tell

	-- Wait for server to start
	delay 2

	-- Open browser
	tell application "System Events"
		open location "http://localhost:8000"
	end tell

	display notification "Server & Sync started" with title "Live Event Photo" subtitle "Admin Panel Opening..."
end run
