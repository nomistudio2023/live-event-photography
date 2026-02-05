# Live Event Photography - System Architecture

**Last Updated**: 2026-02-01  
**Version**: v2.3+

---

## 📐 System Overview

Live Event Photography is a real-time photo publishing system designed for live events. Photos flow from camera to web display in seconds, supporting 2500+ photos and 500+ concurrent viewers.

### Design Goals
- ⚡ Real-time display (< 2 minutes from capture to web)
- 📸 High volume (2500+ photos per event)
- 👥 High concurrency (500+ simultaneous viewers)
- 💾 External storage support (SSD)
- 🔄 Automatic sync to cloud storage
- 🎨 Photo editing capabilities

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LIVE EVENT PHOTOGRAPHY SYSTEM                     │
│                         (Cloudflare R2 Version)                      │
└─────────────────────────────────────────────────────────────────────┘

PHOTOGRAPHER WORKFLOW:
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│  Camera  │───▶│ Admin Panel  │───▶│ photos_web/ │───▶│ R2 Bucket│
│          │    │ localhost:8000│    │  (Local)    │    │ (Cloud)  │
└──────────┘    └──────────────┘    └─────────────┘    └──────────┘
                      │                    │                 │
                      ▼                    ▼                 ▼
                 Upload/Edit         sync_to_r2.py      Auto-update
                 Compress            (Every 3s)         manifest.json

VIEWER WORKFLOW:
┌──────────┐    ┌─────────────────┐    ┌──────────────┐    ┌──────────┐
│ QR Code  │───▶│ Cloudflare Pages│───▶│Pages Function│───▶│ R2 Bucket│
│ / URL    │    │  (index.html)   │    │  /photo/*    │    │          │
└──────────┘    └─────────────────┘    └──────────────┘    └──────────┘
                      │                                         │
                      └─────────────────────────────────────────┘
                              Real-time Photo Display
```

---

## 🔄 Data Flow

### Photo Publishing Flow

```
1. CAPTURE
   📸 Camera → SD Card → photos_buffer/
   
2. SELECTION & EDITING
   Admin UI (localhost:8000)
   ├── View buffer photos
   ├── Select photo
   ├── Apply edits:
   │   ├── Exposure (-2.0 to +2.0)
   │   ├── Rotation (0°, 90°, 180°, 270°)
   │   ├── Straighten (-10° to +10°)
   │   └── Scale (0.5 to 2.0)
   └── Press Enter / Click Publish
   
3. PROCESSING
   server.py
   ├── Apply edits with PIL
   ├── Apply watermark (if enabled)
   ├── Compress & optimize
   ├── Sequential filename (IMG_001.jpg, IMG_002.jpg, ...)
   ├── Save to photos_web/
   └── Update manifest.json
   
4. SYNC TO CLOUD
   sync_to_r2.py (runs every 3 seconds)
   ├── Detect new files in photos_web/
   ├── Upload to R2 (rclone)
   ├── Update R2 manifest.json
   └── Filter hidden files (._, .DS_Store)
   
5. DISPLAY
   index.html
   ├── Fetch manifest.json (every 30s)
   ├── Load new photos
   └── Display in masonry grid
```

### Photo Unpublish Flow

```
1. ADMIN ACTION
   Admin UI → Click Unpublish
   
2. LOCAL DELETION
   server.py
   ├── Move photo from photos_web/ to photos_trash/
   └── Update local manifest.json
   
3. R2 SYNC
   sync_delete_to_r2() (async)
   ├── Delete photo from R2
   ├── Fetch actual R2 photo list
   ├── Update R2 manifest.json
   └── Verify deletion
```

---

## 🗂️ File Structure

```
live-event-photography/
│
├── 📄 Core Backend
│   ├── server.py                 # FastAPI server (1451 lines)
│   ├── sync_to_r2.py             # R2 auto-sync (335 lines)
│   └── r2_manage.py              # R2 management CLI
│
├── 🎨 Frontend
│   ├── index.html                # Event gallery page (762 lines)
│   └── templates/
│       └── admin.html            # Admin UI (1540 lines)
│
├── ⚙️ Configuration
│   ├── config.json               # System config (folders, watermark)
│   └── event_settings.json       # Event page settings (title, hero)
│
├── ☁️ Cloudflare
│   └── functions/
│       └── photo/
│           └── [[path]].js       # R2 proxy function
│
├── 📁 Data Folders (configurable, can be on external SSD)
│   ├── photos_buffer/            # Original photos from camera
│   ├── photos_web/               # Published photos (synced to R2)
│   │   └── manifest.json         # Photo list (reverse chronological)
│   ├── photos_trash/             # Deleted photos
│   └── photos_archive/           # Archived photos
│
├── 🎨 Assets
│   ├── watermark.png             # Watermark image
│   └── hero_bg_*.jpeg            # Hero background images
│
├── 🚀 Launch Scripts
│   ├── start_event.sh            # One-click launcher
│   ├── start_server.sh           # Server launcher
│   ├── start_sync.sh             # Sync launcher
│   └── launcher.applescript      # Mac App launcher
│
├── 🛠️ Utilities
│   ├── cleanup_hidden_files.py   # Remove macOS hidden files
│   ├── fix_r2_manifest.py        # Fix R2 manifest
│   └── cleanup_dot_files.sh      # Shell cleanup script
│
└── 📚 Documentation
    └── docs/                     # All documentation
```

---

## 🔌 System Components

### 1. FastAPI Backend (`server.py`)

**Port**: 8000  
**Framework**: FastAPI + Uvicorn  
**Key Functions**:
- Photo upload and processing
- Image editing (PIL)
- Watermark application
- Manifest management
- Settings management (event, watermark, folders)
- Admin UI serving

**Key APIs**:
- `/api/buffer` - List buffer photos
- `/api/live` - List published photos
- `/api/publish` - Publish with edits
- `/api/unpublish` - Remove published photo
- `/api/event-settings` - Event page settings
- `/api/watermark-settings` - Watermark config
- `/api/folder-settings` - Folder paths

### 2. R2 Sync Script (`sync_to_r2.py`)

**Function**: Automatic sync from local to R2  
**Interval**: 3 seconds  
**Tool**: rclone  
**Mode**: Safe mode (add-only, no auto-delete)

**Process**:
1. Scan photos_web/ for changes
2. Compare with R2 state
3. Upload new photos
4. Update manifest.json
5. Filter hidden files (._, .DS_Store)

### 3. R2 Management Tool (`r2_manage.py`)

**Commands**:
- `list` - List all R2 photos
- `delete <filename>` - Delete single photo
- `delete-multi` - Interactive multi-delete
- `refresh` - Rebuild manifest from R2

### 4. Cloudflare Pages Function

**Path**: `/functions/photo/[[path]].js`  
**R2 Binding**: `GALLERY` → `nomilivegallery`  
**Function**: Proxy R2 objects to `/photo/2026-01-20/*`

**Cache Strategy**:
- Photos: `max-age=31536000` (1 year)
- manifest.json: `max-age=5` (5 seconds)

### 5. Admin UI (`templates/admin.html`)

**Layout**: Three-column design
- **Column 1**: Buffer (candidate photos)
- **Column 2**: Preview + Editor
- **Column 3**: Live Feed (published photos)

**Features**:
- Keyboard shortcuts (Space, Enter, Delete, R, U)
- Real-time statistics
- Sync status indicator
- Settings panel (⚙️ button)

**Settings Panel**:
- Event page settings (title, subtitle, hero image)
- Watermark settings (text/image, position, opacity)
- Folder settings (buffer, web, trash, archive)
- Cleanup tools

### 6. Event Gallery (`index.html`)

**Layout**: Masonry grid (responsive)
- Desktop: 3 columns
- Tablet: 2 columns
- Mobile: 1 column

**Features**:
- Auto-refresh manifest (every 30 seconds)
- Lazy loading images
- Download button per photo
- Dynamic event settings (title, subtitle, hero)
- Error handling (auto-hide failed images)

---

## 🔐 Security & Protection

### Hidden Files Prevention

**Problem**: macOS creates `._*` resource fork files that pollute manifest.

**Solutions**:
1. **Environment Variable**: `COPYFILE_DISABLE=1` in Python scripts
2. **Pre-publish Cleanup**: Remove hidden files before publishing
3. **Manifest Filtering**: Filter during manifest update
4. **R2 Sync Filtering**: Filter during upload
5. **Cleanup Tools**: Manual cleanup scripts

### Image Validation

**Process**:
1. Check file exists
2. Check file size > 0
3. Verify with PIL (image format)
4. Frontend error handling (auto-hide on load failure)

### Safe Mode R2 Sync

**Behavior**: Only add new photos, never auto-delete  
**Reason**: Prevent accidental data loss  
**Manual Delete**: Use `r2_manage.py delete` for intentional deletion

---

## 🛠️ Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pillow (PIL)** - Image processing
- **rclone** - R2 sync tool

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Tailwind CSS** - Utility-first CSS (via CDN)
- **Masonry Layout** - Responsive grid

### Cloud Infrastructure
- **Cloudflare R2** - Object storage (S3-compatible)
- **Cloudflare Pages** - Static site hosting
- **Cloudflare Pages Functions** - Serverless R2 proxy

### Development Tools
- **Git** - Version control
- **AppleScript** - Mac App launcher
- **Shell Scripts** - Automation

---

## 📊 Performance Characteristics

### Latency
- **Camera to Buffer**: Instant (SD card copy)
- **Buffer to Web**: < 5 seconds (edit + process)
- **Web to R2**: < 10 seconds (3s interval + upload)
- **R2 to Viewer**: < 30 seconds (manifest refresh interval)
- **Total**: < 1 minute (camera to viewer)

### Capacity
- **Photos per Event**: 2500+ (tested)
- **Concurrent Viewers**: 500+ (Cloudflare CDN)
- **Storage**: Unlimited (R2 scales automatically)

### Reliability
- **Safe Mode**: Prevents accidental deletion
- **Local Backup**: All photos in photos_web/
- **Error Recovery**: Auto-retry on sync failure
- **Validation**: Multiple layers of image verification

---

## 🔄 Sequential Filename Strategy

**Problem**: Same photo published multiple times should have unique names.

**Solution**:
```python
def get_next_publish_filename(base_name: str, web_folder: str) -> str:
    # First publish: IMG_7109.jpg
    # Second publish: IMG_7109_002.jpg
    # Third publish: IMG_7109_003.jpg
    # ...
```

**Benefits**:
- Unique filenames prevent overwrite
- Easy to track versions
- Maintains chronological order

---

## 🌐 Environment Configuration

### rclone Configuration
```ini
[r2livegallery]
type = s3
provider = Cloudflare
access_key_id = <R2_ACCESS_KEY>
secret_access_key = <R2_SECRET_KEY>
endpoint = https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```

### Cloudflare Pages R2 Binding
```toml
[[r2_buckets]]
binding = "GALLERY"
bucket_name = "nomilivegallery"
```

### Python Environment Variables
```bash
export COPYFILE_DISABLE=1  # Prevent macOS resource forks
```

---

## 🔮 Scalability Considerations

### Current Limits
- **Single Event**: 2500+ photos (tested)
- **Multiple Events**: Manual R2_PATH_PREFIX change required

### Future Enhancements
- **Multi-Event Support**: Auto-switch R2_PATH_PREFIX by date
- **Distributed Processing**: Multiple admin instances
- **Advanced Caching**: Edge cache for manifest
- **Real-time Push**: WebSocket for instant updates

---

## 📝 Design Decisions

### Why R2 instead of GitHub?
- **Capacity**: GitHub has 500 builds/month limit
- **Speed**: R2 is instant, GitHub Pages takes 1-2 minutes
- **Scale**: R2 handles 2500+ photos easily

### Why Safe Mode Sync?
- **Safety**: Prevent accidental deletion of published photos
- **Control**: Explicit deletion via management tool
- **Audit**: Clear record of what was deleted

### Why Sequential Filenames?
- **Versioning**: Track multiple edits of same photo
- **No Overwrite**: Preserve all published versions
- **Simplicity**: Easy to understand and implement

### Why 3-Second Sync Interval?
- **Balance**: Fast enough for real-time, slow enough to batch
- **Efficiency**: Reduces API calls and costs
- **Reliability**: Time for file system to stabilize

---

**For implementation details, see [API_REFERENCE.md](./API_REFERENCE.md)**  
**For usage instructions, see [USER_GUIDE.md](./USER_GUIDE.md)**
