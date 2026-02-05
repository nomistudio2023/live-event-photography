-- Live Event Photo Launcher
-- Starts both server.py and sync_to_r2.py using shell script

on run
	set projectPath to "/Users/nomisas/.gemini/antigravity/scratch/live-event-photography"

	-- Check if server is already running
	set serverRunning to false
	try
		do shell script "lsof -i :8000 | grep LISTEN"
		set serverRunning to true
	end try

	if serverRunning then
		-- Server already running, just open browser
		do shell script "open 'http://localhost:8000'"
		display notification "Opening existing server..." with title "Live Event Photo"
		return
	end if

	-- Use open -a Terminal with shell script to avoid Apple Events permission
	-- Start server in one Terminal window
	do shell script "open -a Terminal '" & projectPath & "/start_server.sh'"

	-- Wait then start sync
	delay 1
	do shell script "open -a Terminal '" & projectPath & "/start_sync.sh'"

	-- Wait for server to start
	delay 2

	-- Open browser
	do shell script "open 'http://localhost:8000'"

	display notification "Server & Sync started" with title "Live Event Photo" subtitle "Admin Panel Opening..."
end run
