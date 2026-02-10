# Changelog

All notable changes to the Live Event Photography project are documented here.

---

## [v2.3+] - 2026-01-23

### 🎉 Major Achievements
- ✅ Core workflow fully functional
- ✅ External SSD support implemented
- ✅ Hidden files issue completely resolved
- ✅ System ready for production use

### ✨ Added
- **Event Settings Management**
  - Customize event title and subtitle
  - Custom hero background image
  - Font customization
  - Real-time updates without server restart
  - API endpoints: `GET/POST /api/event-settings`

- **Watermark System**
  - Text watermark with custom content
  - Image watermark support
  - Position controls (5 positions)
  - Opacity adjustment (0-100%)
  - Size and margin controls
  - API endpoints: `GET/POST /api/watermark-settings`

- **External SSD Support**
  - Dynamic folder path configuration
  - Support for buffer, web, trash, archive folders
  - Auto-create folders if missing
  - Settings saved to config.json
  - API endpoints: `GET/POST /api/folder-settings`

- **Cleanup Tools**
  - `cleanup_hidden_files.py` - Remove macOS hidden files
  - `fix_r2_manifest.py` - Fix R2 manifest
  - `cleanup_dot_files.sh` - Shell script cleanup
  - API endpoint: `POST /api/cleanup-hidden-files`

### 🐛 Fixed
- **Hidden Files Issue**
  - Added `COPYFILE_DISABLE=1` environment variable
  - Automatic filtering of `._*` files in manifest
  - Pre-publish cleanup mechanism
  - Double verification during manifest updates
  - R2 sync filtering

- **Blank Photos Issue**
  - Enhanced image validation (PIL verify)
  - File size check (> 0 bytes)
  - Frontend error handling (auto-hide failed images)
  - Manifest cleanup and verification

- **Cloudflare Deployment**
  - Improved error handling and logging
  - Detailed error messages for Git issues
  - Better frontend error display
  - (Feature currently paused)

### 🔧 Improved
- **Manifest Management**
  - Automatic filtering of hidden files
  - File existence validation
  - Image format verification
  - Reverse chronological sorting

- **Admin UI**
  - Settings panel with tabs
  - Real-time statistics
  - Sync status indicator
  - Keyboard shortcuts
  - Better error messages

### 📝 Documentation
- Created comprehensive documentation structure
- Added user guides and operation manuals
- Created troubleshooting guides
- Added setup and deployment guides

---

## [v2.0] - 2026-01-22

### 🎯 Major Migration
- **GitHub to Cloudflare R2 Migration**
  - Migrated from GitHub Pages to R2 storage
  - Implemented Cloudflare Pages Function for photo serving
  - Achieved real-time sync (seconds instead of minutes)

### ✨ Added
- **R2 Integration**
  - `sync_to_r2.py` - Automatic sync script (3-second interval)
  - `r2_manage.py` - R2 management tool
  - Safe mode (add-only, no auto-delete)
  - Manifest auto-update

- **Cloudflare Pages Function**
  - `/functions/photo/[[path]].js` - R2 proxy
  - Cache control (photos: 1 year, manifest: 5 seconds)
  - R2 binding configuration

- **Launch Scripts**
  - `start_event.sh` - One-click launch
  - `start_server.sh` - Server launcher
  - `start_sync.sh` - Sync launcher
  - Mac App launcher with AppleScript

### 🐛 Fixed
- **Photo Sorting**
  - Fixed new photos appearing at bottom
  - Implemented reverse chronological sorting
  - Consistent sorting across all components

- **Sync Issues**
  - Resolved sync delay issues
  - Fixed manifest caching problems
  - Added timestamp to manifest requests

### 🔧 Improved
- **Performance**
  - Reduced display delay from 1-2 minutes to seconds
  - Eliminated GitHub Pages build limitations
  - Support for 2500+ photos

- **Reliability**
  - Safe mode prevents accidental deletion
  - Automatic retry on sync failure
  - Better error handling

---

## [v1.x] - 2026-01-18 to 2026-01-21

### Initial Development
- Basic photo upload and processing
- Admin UI implementation
- Photo editing features (exposure, rotation, straighten, scale)
- Sequential filename strategy
- Local gallery view
- GitHub Pages integration (later replaced by R2)

### Features Implemented
- FastAPI backend
- PIL image processing
- Three-column admin layout
- Keyboard shortcuts
- Real-time statistics
- Photo archive/delete functionality

---

## Version History Summary

| Version | Date | Key Feature |
|---------|------|-------------|
| v2.3+ | 2026-01-23 | External SSD, Event Settings, Watermark, Hidden Files Fix |
| v2.0 | 2026-01-22 | R2 Migration, Automatic Sync, Real-time Display |
| v1.x | 2026-01-18~21 | Initial Development, Admin UI, Photo Processing |

---

## Upcoming Changes

See [roadmap.md](./roadmap.md) for planned features and improvements.
