# Troubleshooting Guide

Common issues and their solutions for Live Event Photography system.

---

## 🔍 Quick Diagnosis

### System Health Check
```bash
# Check if server is running
curl http://localhost:8000/api/status

# Check if sync is running
ps aux | grep sync_to_r2.py

# Check R2 connection
rclone lsf r2livegallery:nomilivegallery/2026-01-20/

# Check folder permissions
ls -la photos_buffer/ photos_web/
```

---

## 🐛 Common Issues

### 1. Photos Not Appearing on Website

#### Symptom
- Photos published in Admin but not visible on live site
- Manifest.json not updating

#### Possible Causes & Solutions

**A. Sync Script Not Running**
```bash
# Check if running
ps aux | grep sync_to_r2.py

# Start sync script
python3 sync_to_r2.py
```

**B. R2 Connection Issue**
```bash
# Test rclone connection
rclone lsf r2livegallery:nomilivegallery/2026-01-20/

# If fails, reconfigure rclone
rclone config
```

**C. Manifest Cache Issue**
```bash
# Force refresh manifest on R2
python3 r2_manage.py refresh

# Clear browser cache
# Open browser in incognito mode
# Or add ?v=timestamp to URL
```

**D. Hidden Files in Manifest**
```bash
# Clean hidden files
python3 cleanup_hidden_files.py

# Or use shell script
./cleanup_dot_files.sh

# Or use API
curl -X POST http://localhost:8000/api/cleanup-hidden-files
```

---

### 2. Blank/Empty Photos Displayed

#### Symptom
- Photos show as blank spaces on website
- Image load errors in browser console

#### Possible Causes & Solutions

**A. Hidden Files (._* files)**
```bash
# Check manifest for hidden files
cat photos_web/manifest.json | grep "^\._"

# Clean hidden files
python3 cleanup_hidden_files.py

# Fix R2 manifest
python3 fix_r2_manifest.py
```

**B. Corrupted Image Files**
```bash
# Check file sizes
ls -lh photos_web/*.jpg

# Files with 0 bytes are corrupted
# Delete them manually
rm photos_web/corrupted_file.jpg

# Update manifest
python3 r2_manage.py refresh
```

**C. Invalid Image Format**
```python
# Verify images with Python
from PIL import Image
import os

for f in os.listdir('photos_web'):
    if f.endswith('.jpg'):
        try:
            img = Image.open(f'photos_web/{f}')
            img.verify()
            print(f'{f}: OK')
        except Exception as e:
            print(f'{f}: INVALID - {e}')
```

---

### 3. Server Won't Start

#### Symptom
- `python3 server.py` fails
- Port 8000 already in use

#### Solutions

**A. Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn server:app --port 8001
```

**B. Missing Dependencies**
```bash
# Install requirements
pip3 install -r requirements.txt

# Check Python version (need 3.10+)
python3 --version
```

**C. Config File Issues**
```bash
# Check config.json syntax
python3 -m json.tool config.json

# Reset to default if corrupted
cp config.json.backup config.json
```

---

### 4. External SSD Not Working

#### Symptom
- Folder settings not saving
- Photos not saving to SSD
- "Folder not found" errors

#### Solutions

**A. SSD Not Mounted**
```bash
# Check if SSD is mounted
ls /Volumes/

# If not mounted, mount it
# (macOS will usually auto-mount)
```

**B. Incorrect Path**
```bash
# Verify path exists
ls -la /Volumes/YourSSD/photos_buffer

# Create folders if missing
mkdir -p /Volumes/YourSSD/photos_buffer
mkdir -p /Volumes/YourSSD/photos_web
mkdir -p /Volumes/YourSSD/photos_trash
mkdir -p /Volumes/YourSSD/photos_archive
```

**C. Permission Issues**
```bash
# Check permissions
ls -la /Volumes/YourSSD/

# Fix permissions
chmod -R 755 /Volumes/YourSSD/photos_*
```

**D. Need to Restart Server**
```
⚠️ IMPORTANT: After changing folder settings, you MUST restart the server!

1. Stop server.py (Ctrl+C)
2. Stop sync_to_r2.py (Ctrl+C)
3. Restart both
```

---

### 5. Watermark Not Appearing

#### Symptom
- Published photos don't have watermark
- Watermark settings not applied

#### Solutions

**A. Watermark Disabled**
```bash
# Check watermark settings
curl http://localhost:8000/api/watermark-settings

# Enable in Admin UI:
# Settings → Watermark → Enable Watermark
```

**B. Watermark Image Missing**
```bash
# Check if watermark.png exists
ls -la assets/watermark.png

# If missing, add your watermark image
cp your_watermark.png assets/watermark.png
```

**C. Settings Not Saved**
```bash
# Check config.json
cat config.json | grep watermark

# Restart server after changing settings
```

---

### 6. R2 Sync Errors

#### Symptom
- sync_to_r2.py shows errors
- Photos not uploading to R2

#### Solutions

**A. rclone Not Configured**
```bash
# Check rclone config
rclone config show r2livegallery

# If not configured, run setup
rclone config
# Choose: New remote → s3 → Cloudflare R2
```

**B. R2 Credentials Invalid**
```bash
# Test R2 connection
rclone lsf r2livegallery:nomilivegallery/

# If fails, update credentials in rclone config
rclone config update r2livegallery
```

**C. Network Issues**
```bash
# Check internet connection
ping 1.1.1.1

# Check Cloudflare status
curl https://www.cloudflarestatus.com/
```

**D. R2 Bucket Permissions**
```
Check Cloudflare Dashboard:
1. R2 → nomilivegallery
2. Settings → Permissions
3. Ensure API token has read/write access
```

---

### 7. Photos Not Sorting Correctly

#### Symptom
- New photos appear at bottom instead of top
- Photos in wrong order

#### Solutions

**A. Refresh Manifest**
```bash
# Rebuild manifest with correct sorting
python3 r2_manage.py refresh
```

**B. Check Manifest Format**
```bash
# Manifest should be reverse chronological
cat photos_web/manifest.json

# Should show newest photos first
```

**C. Clear Cache**
```
1. Clear browser cache
2. Hard refresh (Cmd+Shift+R on Mac)
3. Or add ?v=timestamp to URL
```

---

### 8. Admin UI Not Loading

#### Symptom
- Admin page blank or not loading
- JavaScript errors in console

#### Solutions

**A. Check Server Status**
```bash
# Verify server is running
curl http://localhost:8000/

# Check server logs for errors
# (Look at terminal where server.py is running)
```

**B. Browser Cache**
```
1. Clear browser cache
2. Hard refresh (Cmd+Shift+R)
3. Try incognito mode
```

**C. JavaScript Errors**
```
1. Open browser console (F12)
2. Check for errors
3. Common issues:
   - CORS errors: Check server.py CORS settings
   - 404 errors: Check file paths
   - Syntax errors: Check recent code changes
```

---

### 9. Mac App Won't Launch

#### Symptom
- Double-clicking Mac App does nothing
- Permission errors

#### Solutions

**A. Permission Issues**
```bash
# Give execute permission
chmod +x "dist/Live Event Photo.app/Contents/MacOS/applet"

# Or rebuild app
./update_mac_app_script.sh
```

**B. AppleScript Errors**
```bash
# Test AppleScript manually
osascript launcher.applescript

# Check for errors in output
```

**C. Terminal Permissions**
```
macOS System Preferences:
1. Security & Privacy
2. Privacy → Automation
3. Allow Terminal to control other apps
```

**D. Use Shell Script Instead**
```bash
# Alternative: Use shell script
./start_event.sh
```

---

### 10. Deployment to Cloudflare Fails

#### Symptom
- Deploy button in Admin shows errors
- Git push fails

#### Solutions

**A. Git Not Configured**
```bash
cd /Users/nomisas/Documents/GitHub/live-event-photography

# Check git status
git status

# Check remote
git remote -v

# If no remote, add it
git remote add origin https://github.com/yourusername/live-event-photography.git
```

**B. Authentication Failed**
```bash
# SSH key method
ssh -T git@github.com

# If fails, generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add to GitHub: Settings → SSH Keys

# OR use Personal Access Token
git remote set-url origin https://TOKEN@github.com/yourusername/repo.git
```

**C. Deployment Feature Paused**
```
⚠️ NOTE: Cloudflare deployment feature is currently paused.

Manual deployment:
1. cd /Users/nomisas/Documents/GitHub/live-event-photography
2. git add .
3. git commit -m "Update settings"
4. git push
5. Wait for Cloudflare Pages auto-deploy (1-3 minutes)
```

---

## 🛠️ Maintenance Tools

### Cleanup Hidden Files
```bash
# Python script (recommended)
python3 cleanup_hidden_files.py

# Shell script
./cleanup_dot_files.sh

# API endpoint
curl -X POST http://localhost:8000/api/cleanup-hidden-files
```

### Fix R2 Manifest
```bash
# Rebuild manifest from actual R2 files
python3 fix_r2_manifest.py
```

### R2 Management
```bash
# List all photos
python3 r2_manage.py list

# Delete single photo
python3 r2_manage.py delete photo.jpg

# Interactive multi-delete
python3 r2_manage.py delete-multi

# Refresh manifest
python3 r2_manage.py refresh
```

### Check Project Status
```bash
# Run status check script
./check_project_status.sh
```

---

## 📊 Log Files

### Server Logs
```bash
# Server output (if running in background)
tail -f server.log

# Or check terminal where server.py is running
```

### Sync Logs
```bash
# Sync output (if running in background)
tail -f sync.log

# Or check terminal where sync_to_r2.py is running
```

### Browser Console
```
1. Open browser (Chrome/Firefox/Safari)
2. Press F12 (or Cmd+Option+I on Mac)
3. Go to Console tab
4. Look for errors (red text)
```

---

## 🆘 Emergency Recovery

### System Completely Broken
```bash
# 1. Stop everything
pkill -f server.py
pkill -f sync_to_r2.py

# 2. Backup current state
cp -r photos_web photos_web.backup
cp config.json config.json.backup

# 3. Clean hidden files
python3 cleanup_hidden_files.py

# 4. Fix manifest
python3 fix_r2_manifest.py

# 5. Restart system
./start_event.sh
```

### Lost All Photos
```bash
# Photos are in multiple places:

# 1. Local backup
ls photos_web/

# 2. R2 backup
rclone ls r2livegallery:nomilivegallery/2026-01-20/

# 3. Trash (if recently deleted)
ls photos_trash/

# Restore from R2
rclone copy r2livegallery:nomilivegallery/2026-01-20/ photos_web/
```

---

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** - Most issues are covered here
2. **Check logs** - Server and sync terminal output
3. **Check browser console** - JavaScript errors
4. **Try restart** - Stop and restart all services

### Information to Provide

When reporting an issue, include:

1. **What you were trying to do**
2. **What happened instead**
3. **Error messages** (exact text)
4. **System info**:
   ```bash
   python3 --version
   rclone version
   sw_vers  # macOS version
   ```
5. **Relevant logs** (server/sync output)

---

## 🔄 Preventive Maintenance

### Daily (During Event)
- [ ] Check sync status indicator (should be green)
- [ ] Monitor server terminal for errors
- [ ] Test photo publish every hour

### After Event
- [ ] Run cleanup: `python3 cleanup_hidden_files.py`
- [ ] Verify R2 manifest: `python3 r2_manage.py list`
- [ ] Backup photos_web folder
- [ ] Clear photos_buffer

### Weekly
- [ ] Update dependencies: `pip3 install -U -r requirements.txt`
- [ ] Check disk space on SSD
- [ ] Review error logs

---

**Still stuck? Check [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details.**
