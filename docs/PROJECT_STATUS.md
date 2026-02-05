# Live Event Photography - Project Status

**Last Updated**: 2026-02-01  
**Version**: v2.3+  
**Status**: ✅ Production Ready

---

## 📊 Current Status

### System Health
- ✅ **Core Workflow**: Camera → Buffer → Admin → Publish → R2 → Live Gallery
- ✅ **Photo Processing**: Exposure, Rotation, Straighten, Scale
- ✅ **External SSD**: Supported and configured
- ✅ **R2 Sync**: Automatic sync every 3 seconds
- ✅ **Hidden Files**: Automatically filtered
- ✅ **Admin UI**: Fully functional with settings panel

### Active Configuration
```
Buffer:  /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_buffer
Web:     /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web
Trash:   /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_trash
Archive: /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_archive
```

---

## 🎯 Core Features

### ✅ Completed Features
1. **Photo Management**
   - Upload to buffer
   - Edit (exposure, rotation, straighten, scale)
   - Publish to web folder
   - Sequential filename strategy (IMG_001.jpg, IMG_002.jpg, etc.)
   - Archive/delete photos

2. **R2 Integration**
   - Automatic sync to Cloudflare R2
   - Safe mode (add-only, no auto-delete)
   - Manifest management
   - Cloudflare Pages Function proxy

3. **External SSD Support**
   - Dynamic folder path configuration
   - Auto-create folders if missing
   - Settings saved to config.json

4. **Event Settings**
   - Customize event title/subtitle
   - Custom hero background image
   - Font customization
   - Real-time updates (no server restart needed)

5. **Watermark System**
   - Text watermark with custom content
   - Image watermark support
   - Position, opacity, size, margin controls
   - Enable/disable toggle

6. **Admin UI**
   - Three-column layout (Buffer / Preview+Editor / Live Feed)
   - Keyboard shortcuts (Space, Enter, Delete, R, U)
   - Real-time statistics
   - Sync status indicator
   - Settings panel

### ⏸️ Paused Features
- Watermark advanced options (font selection, visual positioning)
- Cloudflare one-click deployment (code preserved)

---

## 🚀 Quick Start

### Launch System
```bash
# Option 1: Shell script
./start_event.sh

# Option 2: Mac App
# Double-click: dist/Live Event Photo.app

# Option 3: Manual
python3 server.py        # Terminal 1
python3 sync_to_r2.py    # Terminal 2
```

### Access Points
- **Admin Panel**: http://localhost:8000
- **Local Gallery**: http://localhost:8000/gallery
- **Live Site**: https://live-event-photography.pages.dev

---

## 📁 Project Structure

```
live-event-photography/
├── server.py                 # FastAPI backend (1451 lines)
├── sync_to_r2.py             # R2 auto-sync (335 lines)
├── r2_manage.py              # R2 management tool
├── index.html                # Event gallery page (762 lines)
├── templates/
│   └── admin.html            # Admin UI (1540 lines)
├── config.json               # System configuration
├── event_settings.json       # Event page settings
├── functions/
│   └── photo/[[path]].js     # Cloudflare Pages Function
├── assets/
│   ├── watermark.png         # Watermark image
│   └── hero_bg_*.jpeg        # Hero background images
└── docs/                     # Documentation (see below)
```

---

## 🔧 API Endpoints

| Endpoint | Method | Function |
|----------|--------|----------|
| `/api/buffer` | GET | List buffer photos |
| `/api/live` | GET | List published photos |
| `/api/publish` | POST | Publish photo with edits |
| `/api/unpublish` | POST | Remove published photo |
| `/api/archive` | POST | Archive photo |
| `/api/reject` | POST | Delete photo |
| `/api/status` | GET | System status |
| `/api/event-settings` | GET/POST | Event page settings |
| `/api/watermark-settings` | GET/POST | Watermark settings |
| `/api/folder-settings` | GET/POST | Folder paths |
| `/api/cleanup-hidden-files` | POST | Clean hidden files |
| `/live/{filename}` | GET | No-cache photo serving |

---

## 🛡️ Protection Mechanisms

### Hidden Files Prevention
1. **Environment Variable**: `COPYFILE_DISABLE=1` in server.py and sync_to_r2.py
2. **Pre-publish Cleanup**: Automatic removal before publishing
3. **Manifest Filtering**: Double-check during manifest updates
4. **R2 Sync Filtering**: Filter during upload to R2

### Image Validation
1. File existence check
2. File size check (> 0 bytes)
3. PIL image format verification
4. Frontend error handling (auto-hide failed images)

---

## ⚠️ Known Issues

### 1. Online HTML Not Updated
**Status**: Pending investigation  
**Issue**: Local `index.html` is fixed, but Cloudflare Pages may not have deployed the latest version.

**Possible Causes**:
- Cloudflare Pages deployment not triggered
- Browser/CDN cache
- Pages settings using different HTML file

**Next Steps**:
1. Check Cloudflare Dashboard → Pages → Deployments
2. Test with incognito mode or `?v=timestamp` parameter
3. Verify Pages Build Output Directory setting

---

## 📚 Documentation Index

All documentation is now organized in the `docs/` folder:

### Core Documentation
- **PROJECT_STATUS.md** (this file) - Current project status
- **ARCHITECTURE.md** - System architecture and data flow
- **API_REFERENCE.md** - Complete API documentation
- **USER_GUIDE.md** - User operation manual

### Development Documentation
- **CHANGELOG.md** - Version history and changes
- **DEVELOPMENT_ROADMAP.md** - Future development plans
- **TROUBLESHOOTING.md** - Common issues and solutions

### Setup Guides
- **SETUP_GUIDE.md** - Initial setup instructions
- **DEPLOYMENT_GUIDE.md** - Cloudflare deployment guide
- **R2_SETUP_GUIDE.md** - R2 configuration guide

---

## 🎯 Next Steps

### High Priority
1. Fix online event page HTML update issue
2. Test complete workflow with external SSD
3. Verify R2 sync stability

### Medium Priority
1. Watermark advanced options
2. Cloudflare one-click deployment fix

### Low Priority
1. Batch publish with individual edit params
2. EXIF metadata preservation
3. Mobile admin UI

---

## 📊 Statistics

### Code Size
- Total Lines: ~4,087 (core code)
- Python: ~2,200 lines
- HTML/JS: ~1,887 lines

### Feature Completion
- Core Features: 100%
- External SSD: 100%
- Hidden Files Fix: 100%
- Watermark: 70%
- Deployment: 80%

---

**For detailed information, see the documentation in the `docs/` folder.**
