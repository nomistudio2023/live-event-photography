Perplexity:
---

# Live Event Photography - 開發進度 Compact

## 專案架構

text

`live-event-photography/ ├── server.py              # FastAPI 後端服務器 ├── sync_to_r2.py          # R2 自動同步腳本 ├── r2_manage.py           # R2 照片管理工具 ├── start_event.sh         # 一鍵啟動腳本 ├── launcher.applescript   # Mac App 啟動器 ├── photos_buffer/         # 原始照片暫存 ├── photos_web/            # 已發布照片（同步到 R2） ├── templates/ │   └── admin.html         # Admin 管理後台 └── functions/     └── photo/[[path]].js  # Cloudflare Function (R2 代理)`

---

## 核心功能模組

## 1. **照片處理流程**

text

`📸 相機 → photos_buffer → Admin 選擇/編輯 → photos_web → R2 同步 → 網站顯示`

## 2. **照片編輯功能** (`server.py`)

- **Exposure**: `-2.0 ~ +2.0` 曝光調整
    
- **Rotation**: `0°, 90°, 180°, 270°` 旋轉
    
- **Straighten**: `-10° ~ +10°` 水平校正
    
- **Scale**: `0.5 ~ 2.0` 縮放
    

**API 端點**: `POST /api/publish`

python

`{   "filename": "IMG_1234.jpg",  "exposure": 0.5,  "rotation": 90,  "straighten": -2.5,  "scale": 1.2 }`

## 3. **R2 存儲整合**

**存儲架構**:

- **Bucket**: `nomilivegallery`
    
- **路徑**: `/photo/2026-01-20/*.jpg`
    
- **Manifest**: `/photo/2026-01-20/manifest.json`
    

**Cloudflare Function** (`functions/photo/[[path]].js`):

javascript

`// R2 綁定名稱: GALLERY const object = await env.GALLERY.get(path); headers.set('Cache-Control', 'public, max-age=31536000');`

**同步腳本** (`sync_to_r2.py`):

- **安全模式**: 只新增照片，不自動刪除 R2 上的照片 (`SAFE_MODE = True`)
    
- **檢查間隔**: 每 3 秒掃描 `photos_web/`
    
- **自動更新 manifest**: 按時間倒序排列
    

---

## 關鍵問題與解決方案

## ❌ **問題 1: 同張照片重複發布無法更新**

**原因**: 瀏覽器/Server 緩存機制

**解決方案**:

python

`# server.py - 自定義 /live/ 端點，強制 no-cache @app.get("/live/{filename:path}") async def serve_live_image(filename: str):     return FileResponse(        file_path,        media_type="image/jpeg",        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}    )`

javascript

`// admin.html - 前端加時間戳 <img src="/live/${item.filename}?t=${new Date().getTime()}">`

## ❌ **問題 2: R2 manifest 緩存問題**

**原因**: 瀏覽器緩存 manifest.json，導致新照片不顯示

**解決方案**:

javascript

``// index.html - 加時間戳繞過緩存 const response = await fetch(`${MANIFEST_URL}?t=${new Date().getTime()}`);``

## ❌ **問題 3: R2 同步可能誤刪照片**

**解決方案**:

python

`# sync_to_r2.py - 安全模式 SAFE_MODE = True  # 只新增不刪除 # 如需刪除，使用管理工具 python3 r2_manage.py list          # 列出所有照片 python3 r2_manage.py delete IMG_1.jpg  # 刪除指定照片`

---

## API 端點總覽

|端點|方法|功能|輸入|輸出|
|---|---|---|---|---|
|`/api/buffer`|GET|列出 photos_buffer 照片|-|`{files: [...]}`|
|`/api/live`|GET|列出 photos_web 照片|-|`{images: [...]}`|
|`/api/publish`|POST|發布照片到 photos_web|`{filename, exposure, rotation, straighten, scale}`|`{success: true, dest: "..."}`|
|`/api/unpublish`|POST|移除 photos_web 照片|`{filename}`|`{success: true}`|
|`/api/archive`|POST|封存照片到 archive|`{filename}`|`{success: true}`|
|`/api/status`|GET|系統狀態（含 sync 狀態）|-|`{server: true, sync: bool}`|
|`/live/{filename}`|GET|無緩存照片服務|-|照片檔案|

---

## Admin UI 核心功能

## **三欄佈局**

text

`┌─────────────┬───────────────────┬────────────┐ │ COL 1       │ COL 2             │ COL 3      │ │ Buffer      │ Preview + Editor  │ Live Feed  │ │ (候選照片)   │ (編輯器)           │ (已發布)    │ └─────────────┴───────────────────┴────────────┘`

## **快捷鍵**

- `Space` / `→`: 下一張
    
- `Enter`: 發布
    
- `Delete` / `Backspace`: 封存
    
- `R`: 順時針旋轉 90°
    
- `U`: Unpublish（移除已發布）
    

## **實時統計**

javascript

``document.getElementById('stats-buffer').innerText = `Buffer: ${count}`; document.getElementById('stats-live').innerText = `Live: ${count}`; document.getElementById('stats-published').innerText = sessionStats.published;``

## **同步狀態指示器**

xml

`<div id="sync-status">   <span id="sync-indicator" class="w-2 h-2 rounded-full"></span>  <span id="sync-text">Sync</span> </div>`

- 🟢 **Syncing**: sync_to_r2.py 運行中
    
- 🟡 **Offline**: 未啟動同步腳本
    

---

## 一鍵啟動方式

## **方式 1: Shell 腳本**

bash

`./start_event.sh`

- 同時啟動 `server.py` 和 `sync_to_r2.py`
    
- 自動開啟瀏覽器至 `http://localhost:8000`
    

## **方式 2: Mac App**

雙擊 `dist/Live Event Photo.app`

- 使用 AppleScript 啟動
    
- 自動分割 Terminal 標籤頁
    
- 標籤名稱: `Live Event Photo - Server` / `Sync`
    

---

## 照片發布最佳實踐

## **工作流程**

1. **拍攝照片** → 自動進入 `photos_buffer/`
    
2. **打開 Admin** → `http://localhost:8000`
    
3. **選擇 & 編輯** → 調整曝光/旋轉/水平
    
4. **按 Enter 發布** → 照片進入 `photos_web/`
    
5. **自動同步到 R2** → `sync_to_r2.py` 偵測變化並上傳
    
6. **網站即時顯示** → 訪客立即看到新照片（無需等待 Git build）
    

## **注意事項**

- ✅ 同一張照片可多次調整參數後重新發布
    
- ✅ R2 上的照片會保留（安全模式）
    
- ⚠️ 如需刪除 R2 照片，使用 `r2_manage.py`
    
- ⚠️ 確保 `sync_to_r2.py` 保持運行狀態
    

---

## 環境變數配置

**Cloudflare Pages R2 Binding**:

text

`# wrangler.toml (已配置) [[r2_buckets]] binding = "GALLERY" bucket_name = "nomilivegallery"`

**Python 腳本環境**:

bash

`# 需要 AWS CLI 認證（用於 rclone） rclone config show cloudflare-r2`

---

## 待優化項目

1. **Sequential Filename 策略**: 同一照片多次發布時的命名邏輯（目前直接覆蓋）
    
2. **Batch Publish**: 多選照片批量發布功能
    
3. **R2 Manifest 緩存**: 考慮使用 Edge Cache API 改善載入速度
    
4. **Mobile Admin UI**: 適配手機版管理介面
    
5. **照片 Metadata**: 保留 EXIF 資訊（目前會被 Pillow 處理掉）
    

---

這份 Compact 涵蓋了 Live Event Photography 的核心架構、API、問題解決方案和操作流程，可以直接提供給 LLM 作為後續開發的 Context。