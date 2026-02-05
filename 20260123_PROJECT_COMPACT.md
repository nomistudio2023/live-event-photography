# Live Event Photography - 專案 Compact 報告
**日期**: 2026-01-23  
**版本**: v2.3+ (1小時完成版本)  
**狀態**: ✅ 核心功能完成，可立即使用於活動

---

## 📐 專案架構

### 系統流程
```
📸 相機拍攝
    ↓
photos_buffer/ (外接SSD: /Volumes/詠松-2Tssd/.../photos_buffer)
    ↓
Admin 後台 (localhost:8000) - 選擇/編輯照片
    ↓
photos_web/ (外接SSD: /Volumes/詠松-2Tssd/.../photos_web)
    ↓
sync_to_r2.py 自動同步 (每3秒檢查)
    ↓
Cloudflare R2 (nomilivegallery/2026-01-20/)
    ↓
Cloudflare Pages Function (functions/photo/[[path]].js)
    ↓
活動頁面顯示 (live-event-photography.pages.dev)
```

### 核心文件結構
```
live-event-photography/
├── server.py              # FastAPI 後端服務器 (1451 行)
├── sync_to_r2.py          # R2 自動同步腳本 (335 行)
├── index.html             # 活動頁面 (762 行)
├── templates/
│   └── admin.html         # Admin 管理後台 (1540 行)
├── config.json            # 系統配置（資料夾路徑、浮水印等）
├── event_settings.json    # 活動頁面設定（標題、副標題、背景圖片）
├── photos_buffer/         # 原始照片暫存（外接SSD）
├── photos_web/            # 已發布照片（外接SSD，同步到 R2）
├── photos_trash/          # 已刪除照片
├── photos_archive/        # 封存照片
└── functions/
    └── photo/[[path]].js  # Cloudflare Function (R2 代理)
```

---

## ✅ 已完成的核心功能

### 1. 照片處理流程 ✅
- ✅ 照片自動進入 `photos_buffer/`
- ✅ Admin 後台選擇和編輯照片
- ✅ 發布到 `photos_web/`
- ✅ 自動同步到 Cloudflare R2
- ✅ 活動頁面即時顯示

### 2. 照片編輯功能 ✅
- ✅ **Exposure**: -2.0 ~ +2.0（曝光調整）
- ✅ **Rotation**: 0°, 90°, 180°, 270°（旋轉）
- ✅ **Straighten**: -10° ~ +10°（水平校正）
- ✅ **Scale**: 0.5 ~ 2.0（縮放）

**API 端點**: `POST /api/publish`

### 3. Sequential Filename 策略 ✅
- ✅ 同一照片多次發布自動產生序號
- ✅ 第一次：`15D_7109.jpg`
- ✅ 第二次：`15D_7109_002.jpg`
- ✅ 第三次：`15D_7109_003.jpg`

### 4. 外接SSD支援 ✅
- ✅ 支援動態設定資料夾路徑
- ✅ 當前路徑：`/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/`
- ✅ `sync_to_r2.py` 自動讀取 `config.json` 中的路徑
- ✅ Admin 面板可設定資料夾路徑

### 5. R2 同步機制 ✅
- ✅ `sync_to_r2.py` 自動同步腳本
- ✅ 每 3 秒檢查 `photos_web/` 變化
- ✅ 自動上傳新照片到 R2
- ✅ 自動更新 R2 manifest.json
- ✅ 過濾隱藏文件（._ 開頭）

### 6. Admin UI ✅
- ✅ 三欄佈局（Buffer / Preview / Live Feed）
- ✅ 快捷鍵支援（Space, Enter, Delete, R, U）
- ✅ 實時統計（Buffer/Live 照片數量）
- ✅ 同步狀態指示器（🟢 Syncing / 🟡 Offline）
- ✅ 系統設定面板（活動設定、浮水印、資料夾）

---

## 🔧 今日修復的問題

### 1. 空白照片問題 ✅
**問題**: manifest.json 包含 macOS 隱藏文件（._ 開頭），導致活動頁顯示空白

**修復**:
- ✅ `update_manifest()` 函數過濾隱藏文件
- ✅ 發布時自動清理隱藏文件
- ✅ 前端錯誤處理（載入失敗自動隱藏）
- ✅ 創建清理工具 `cleanup_hidden_files.py`

### 2. macOS 隱藏文件問題 ✅
**問題**: macOS 自動產生 `._` 開頭的文件，污染 manifest.json

**修復**:
- ✅ 設置 `COPYFILE_DISABLE=1` 環境變數（server.py, sync_to_r2.py）
- ✅ 發布前自動清理隱藏文件
- ✅ manifest 更新時自動過濾
- ✅ R2 同步時自動過濾
- ✅ 創建修復工具 `fix_r2_manifest.py`

### 3. 活動頁面 HTML 修復 ✅
**問題**: 
- 左上角多出符號（多餘的 `)` 字元）
- 標題左側有藍色裝飾條（`.section-title::before`）

**修復**:
- ✅ 移除多餘的 `)` 字元
- ✅ 移除 `.section-title::before` CSS
- ✅ 恢復舊版圖片路徑邏輯（本地/線上自動切換）

---

## 📋 當前系統狀態

### 功能狀態
- ✅ **照片發布**: 正常運作
- ✅ **活動頁顯示**: 正常，無空白圖片
- ✅ **manifest.json**: 乾淨（無隱藏文件）
- ✅ **R2 同步**: 正常運作
- ✅ **外接SSD**: 已設定並可用

### 資料夾路徑（當前設定）
```
Buffer:  /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_buffer
Web:     /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web
Trash:   /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_trash
Archive: /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_archive
```

### 防護機制
- ✅ 自動清理隱藏文件
- ✅ 自動過濾 manifest
- ✅ 雙重驗證機制
- ✅ 環境變數禁用資源分叉

---

## 🛠️ 核心 API 端點

| 端點 | 方法 | 功能 | 輸入 | 輸出 |
|------|------|------|------|------|
| `/api/buffer` | GET | 列出 buffer 照片 | - | `{files: [...]}` |
| `/api/live` | GET | 列出已發布照片 | - | `{images: [...]}` |
| `/api/publish` | POST | 發布照片 | `{filename, exposure, rotation, straighten, scale}` | `{status: "success", published_as: "..."}` |
| `/api/unpublish` | POST | 下架照片 | `{filename}` | `{status: "unpublished"}` |
| `/api/archive` | POST | 封存照片 | `{filename}` | `{status: "archived"}` |
| `/api/reject` | POST | 刪除照片 | `{filename}` | `{status: "rejected"}` |
| `/api/status` | GET | 系統狀態 | - | `{server: true, sync: bool}` |
| `/api/event-settings` | GET/POST | 活動設定 | - | `{event_title, event_subtitle, ...}` |
| `/api/watermark-settings` | GET/POST | 浮水印設定 | - | `{enabled, type, position, ...}` |
| `/api/folder-settings` | GET/POST | 資料夾設定 | - | `{buffer_folder, web_folder, ...}` |
| `/api/cleanup-hidden-files` | POST | 清理隱藏文件 | - | `{status: "success", removed_files: [...]}` |
| `/live/{filename}` | GET | 無緩存照片服務 | - | 照片檔案 |

---

## 🎨 Admin UI 功能

### 三欄佈局
```
┌─────────────┬───────────────────┬────────────┐
│ COL 1       │ COL 2             │ COL 3      │
│ Buffer      │ Preview + Editor  │ Live Feed  │
│ (候選照片)   │ (編輯器)           │ (已發布)    │
└─────────────┴───────────────────┴────────────┘
```

### 快捷鍵
- `Space` / `→`: 下一張
- `Enter`: 發布
- `Delete` / `Backspace`: 封存
- `R`: 順時針旋轉 90°
- `U`: Unpublish（移除已發布）

### 系統設定（⚙️ 設定按鈕）
1. **活動頁面設定**
   - 標題、副標題
   - 字型、字體大小
   - 背景圖片（URL 或本地上傳）

2. **浮水印設定**
   - 啟用/停用
   - 類型（圖片/文字）
   - 位置、透明度、大小、邊距
   - 本地上傳浮水印圖片

3. **資料夾設定**
   - 設定外接SSD路徑
   - 更改後需重啟服務器

4. **清理工具**
   - 一鍵清理隱藏文件
   - 自動更新 manifest

---

## 🚀 啟動方式

### 方式 1: Shell 腳本
```bash
./start_event.sh
```
- 同時啟動 `server.py` 和 `sync_to_r2.py`
- 自動開啟瀏覽器至 `http://localhost:8000`

### 方式 2: Mac App
雙擊 `dist/Live Event Photo.app`
- 使用 AppleScript 啟動
- 自動分割 Terminal 標籤頁

### 方式 3: 手動啟動
```bash
# Terminal 1
python3 server.py

# Terminal 2
python3 sync_to_r2.py
```

---

## 📊 R2 存儲架構

### 配置
- **Bucket**: `nomilivegallery`
- **路徑前綴**: `2026-01-20`
- **R2 綁定**: `GALLERY` (在 Cloudflare Pages Function 中)

### Cloudflare Function
**文件**: `functions/photo/[[path]].js`

**功能**:
- 代理 R2 照片到 `/photo/2026-01-20/*.jpg`
- 設定緩存策略：
  - 照片：`max-age=31536000` (1年)
  - manifest.json：`max-age=5` (5秒)

### 同步腳本
**文件**: `sync_to_r2.py`

**功能**:
- 每 3 秒檢查 `photos_web/` 變化
- 自動上傳新照片到 R2
- 自動更新 R2 manifest.json
- 過濾隱藏文件（._ 開頭）

---

## 🛡️ 防護機制

### 1. 隱藏文件防護
- ✅ `COPYFILE_DISABLE=1` 環境變數（防止產生）
- ✅ 發布前自動清理
- ✅ manifest 更新時自動過濾
- ✅ R2 同步時自動過濾
- ✅ 清理工具（`cleanup_hidden_files.py`, `fix_r2_manifest.py`）

### 2. 圖片驗證
- ✅ 文件存在性檢查
- ✅ 文件大小檢查（> 0）
- ✅ PIL 圖片格式驗證
- ✅ 前端錯誤處理（載入失敗自動隱藏）

### 3. Manifest 管理
- ✅ 自動過濾隱藏文件
- ✅ 驗證文件存在性
- ✅ 移除不存在的文件條目
- ✅ 按時間倒序排列

---

## ⏸️ 已暫停的功能

### 1. 浮水印細節修訂
- ⏸️ 文字浮水印字型選擇
- ⏸️ 浮水印位置圖形化操作
- ✅ 基本功能已實現（可開關、位置選擇、透明度等）

### 2. Cloudflare 一鍵部署
- ⏸️ 部署功能已實現但暫停使用
- ⏸️ 留待未來處理
- ✅ 代碼已保留，可隨時啟用

---

## 🔍 已知問題

### 1. 線上活動頁面 HTML 未更新 ⚠️
**狀態**: 待修復  
**問題**: 
- 本地 `index.html` 已修復（移除符號、恢復舊版圖片路徑）
- GitHub repo 已有 `index.html`（已複製）
- 但 Cloudflare Pages 可能未觸發新部署或使用緩存

**可能原因**:
- Cloudflare Pages 未觸發新部署
- 瀏覽器/CDN 緩存
- Pages 設定使用其他 HTML 文件

**建議檢查**:
1. Cloudflare Dashboard → Pages → Deployments（確認有新部署）
2. 使用無痕模式或加 `?v=timestamp` 參數測試
3. 確認 Pages 設定中的 Build Output Directory

---

## 📁 重要文件

### 設定文件
- `config.json` - 系統配置（資料夾路徑、浮水印等）
- `event_settings.json` - 活動頁面設定

### 核心代碼
- `server.py` - FastAPI 後端服務器
- `sync_to_r2.py` - R2 自動同步腳本
- `index.html` - 活動頁面
- `templates/admin.html` - Admin 管理後台

### 工具腳本
- `cleanup_hidden_files.py` - 清理隱藏文件工具
- `fix_r2_manifest.py` - 修復 R2 manifest 工具
- `cleanup_dot_files.sh` - 使用 dot_clean 清理腳本

### 教學文檔
- `MANUAL_HTML_SETTINGS_GUIDE.md` - 手動修改HTML教學
- `OPERATION_MANUAL.md` - 操作手冊
- `DEPLOYMENT_GUIDE.md` - 部署功能說明（暫停使用）

### 狀態報告
- `SUCCESS_REPORT_20260123.md` - 問題修復成功報告
- `CURRENT_STATUS_20260123.md` - 當前專案狀態
- `FINAL_STATUS_20260123.md` - 最終狀態報告

---

## 🎯 下次開發重點

### 高優先級
1. **修復線上活動頁面 HTML**
   - 確認 Cloudflare Pages 部署狀態
   - 檢查 Pages 設定
   - 驗證 HTML 文件路徑

2. **測試外接SSD完整流程**
   - 確認所有功能在外接SSD上正常運作
   - 測試路徑變更後的同步

### 中優先級
1. **浮水印細節優化**
   - 文字浮水印字型選擇
   - 浮水印位置圖形化操作

2. **Cloudflare 一鍵部署**
   - 修復部署功能
   - 測試 Git 認證

### 低優先級
1. **Batch Publish 增強**
   - 支援每張照片獨立設定編輯參數

2. **EXIF Metadata 保留**
   - 保留照片原始資訊

---

## 📊 專案統計

### 代碼規模
- `server.py`: 1451 行
- `templates/admin.html`: 1540 行
- `index.html`: 762 行
- `sync_to_r2.py`: 335 行

### 功能完成度
- ✅ 核心功能: 100%
- ✅ 外接SSD支援: 100%
- ✅ 隱藏文件修復: 100%
- ⏸️ 浮水印優化: 70%
- ⏸️ 部署功能: 80%

---

## 🔑 關鍵技術點

### 1. 環境變數設置
```python
# server.py, sync_to_r2.py
os.environ['COPYFILE_DISABLE'] = '1'  # 禁用 macOS 資源分叉
```

### 2. Manifest 更新邏輯
```python
def update_manifest():
    # 1. 清理隱藏文件
    # 2. 掃描有效照片
    # 3. 驗證圖片有效性
    # 4. 最終過濾（雙重檢查）
    # 5. 保存 manifest.json
```

### 3. 圖片路徑自動切換
```javascript
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const MANIFEST_URL = isLocal ? 'photos_web/manifest.json' : '/photo/2026-01-20/manifest.json';
const IMAGE_BASE_URL = isLocal ? 'photos_web/' : '/photo/2026-01-20/';
```

### 4. R2 同步過濾
```python
# sync_to_r2.py
filtered_photos = {
    p for p in photos
    if not p.startswith('._') and p != '.DS_Store' and p != 'manifest.json'
}
```

---

## 🚨 重要提醒

### 1. 重啟服務器
- 更改 `config.json` 後必須重啟服務器
- 環境變數只在程序啟動時生效

### 2. 定期清理
- 建議每天活動結束後執行 `python3 cleanup_hidden_files.py`
- 如果發現 manifest 包含隱藏文件，執行 `python3 fix_r2_manifest.py`

### 3. 外接SSD
- 確保外接SSD已連接
- 確認路徑設定正確
- 更改路徑後重啟服務器

---

## 📝 待處理事項

### 立即處理
- [ ] 修復線上活動頁面 HTML 更新問題
- [ ] 確認 Cloudflare Pages 部署狀態

### 未來處理
- [ ] 浮水印細節優化
- [ ] Cloudflare 一鍵部署修復
- [ ] Batch Publish 增強
- [ ] EXIF Metadata 保留

---

---

## 📚 相關文檔索引

### 狀態報告
- `SUCCESS_REPORT_20260123.md` - 問題修復成功報告
- `CURRENT_STATUS_20260123.md` - 當前專案狀態
- `FINAL_STATUS_20260123.md` - 最終狀態報告
- `project_status_20260122.md` - 2026-01-22 狀態報告

### 修復記錄
- `BUGFIXES_20260123.md` - Bug 修復報告
- `HIDDEN_FILES_FIX_FINAL.md` - 隱藏文件問題最終修復
- `R2_MANIFEST_FIX.md` - R2 manifest 修復
- `QUICK_FIX_SUMMARY.md` - 快速修復總結

### 功能改進
- `IMPROVEMENTS_20260123.md` - 功能改進總結
- `FEATURES_IMPLEMENTED_20260123.md` - 已實現功能

### 使用指南
- `MANUAL_HTML_SETTINGS_GUIDE.md` - 手動修改HTML教學
- `OPERATION_MANUAL.md` - 操作手冊
- `CLEANUP_USAGE.md` - 清理工具使用說明
- `MACOS_HIDDEN_FILES_SOLUTION.md` - macOS 隱藏文件解決方案
- `RESTART_INSTRUCTIONS.md` - 重啟服務器說明

### 部署相關
- `DEPLOYMENT_GUIDE.md` - 部署功能說明
- `R2_SETUP_GUIDE.md` - R2 設定指南

### 開發路線圖
- `DEVELOPMENT_ROADMAP.md` - 後續開發路線圖
- `NEXT_STEPS.md` - 下一步計劃

---

## 📊 專案統計

### 代碼規模
- **總行數**: 約 4,087 行（核心代碼）
- **server.py**: 1,451 行
- **templates/admin.html**: 1,540 行
- **index.html**: 762 行
- **sync_to_r2.py**: 335 行

### 文檔數量
- **Markdown 文檔**: 29 個
- **工具腳本**: 6 個（cleanup, fix, start 等）

### 功能完成度
- ✅ **核心功能**: 100%
- ✅ **外接SSD支援**: 100%
- ✅ **隱藏文件修復**: 100%
- ✅ **空白照片修復**: 100%
- ⏸️ **浮水印優化**: 70%
- ⏸️ **部署功能**: 80%

---

## 🎯 下次開發重點

### 立即處理（高優先級）
1. **修復線上活動頁面 HTML 更新問題**
   - 確認 Cloudflare Pages 部署狀態
   - 檢查 Pages 設定（Build Output Directory）
   - 驗證 HTML 文件路徑
   - 測試瀏覽器/CDN 緩存

2. **測試外接SSD完整流程**
   - 確認所有功能在外接SSD上正常運作
   - 測試路徑變更後的同步
   - 驗證隱藏文件清理機制

### 未來處理（中優先級）
1. **浮水印細節優化**
   - 文字浮水印字型選擇
   - 浮水印位置圖形化操作

2. **Cloudflare 一鍵部署修復**
   - 修復 Git 認證問題
   - 測試部署流程

### 優化項目（低優先級）
1. **Batch Publish 增強**
   - 支援每張照片獨立設定編輯參數

2. **EXIF Metadata 保留**
   - 保留照片原始資訊

3. **Mobile Admin UI**
   - 適配手機版管理介面

---

## 🔑 關鍵技術點總結

### 1. 環境變數設置
```python
# server.py, sync_to_r2.py
os.environ['COPYFILE_DISABLE'] = '1'  # 禁用 macOS 資源分叉
```

### 2. Manifest 更新邏輯
```python
def update_manifest():
    # 1. 清理隱藏文件（發布前）
    # 2. 掃描有效照片（過濾隱藏文件）
    # 3. 驗證圖片有效性（PIL verify）
    # 4. 最終過濾（雙重檢查）
    # 5. 保存 manifest.json
```

### 3. 圖片路徑自動切換
```javascript
const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1';
const MANIFEST_URL = isLocal ? 'photos_web/manifest.json' : 
                                '/photo/2026-01-20/manifest.json';
const IMAGE_BASE_URL = isLocal ? 'photos_web/' : '/photo/2026-01-20/';
```

### 4. R2 同步過濾
```python
# sync_to_r2.py
filtered_photos = {
    p for p in photos
    if not p.startswith('._') and p != '.DS_Store' and p != 'manifest.json'
}
```

### 5. Sequential Filename
```python
# server.py
def get_next_publish_filename(base_name: str, web_folder: str) -> str:
    # 第一次: 15D_7109.jpg
    # 第二次: 15D_7109_002.jpg
    # 第三次: 15D_7109_003.jpg
```

---

## 🚨 重要提醒

### 1. 重啟服務器
- ✅ 更改 `config.json` 後必須重啟服務器
- ✅ 環境變數只在程序啟動時生效
- ✅ 修改代碼後需要重啟

### 2. 定期維護
- ✅ 建議每天活動結束後執行 `python3 cleanup_hidden_files.py`
- ✅ 如果發現 manifest 包含隱藏文件，執行 `python3 fix_r2_manifest.py`
- ✅ 檢查 R2 同步狀態

### 3. 外接SSD
- ✅ 確保外接SSD已連接
- ✅ 確認路徑設定正確（`/Volumes/詠松-2Tssd/...`）
- ✅ 更改路徑後重啟服務器

### 4. 線上部署
- ⚠️ 本地修改 `index.html` 後，需要同步到 GitHub repo
- ⚠️ 推送到 GitHub 後，Cloudflare Pages 會自動部署
- ⚠️ 可能需要等待幾分鐘才能看到更新

---

## 📝 待處理事項清單

### 立即處理
- [ ] 修復線上活動頁面 HTML 更新問題
  - [ ] 確認 Cloudflare Pages 部署狀態
  - [ ] 檢查 Pages 設定
  - [ ] 驗證 HTML 文件路徑
  - [ ] 測試緩存清除

### 未來處理
- [ ] 浮水印細節優化
- [ ] Cloudflare 一鍵部署修復
- [ ] Batch Publish 增強
- [ ] EXIF Metadata 保留
- [ ] Mobile Admin UI 適配

---

**最後更新**: 2026-01-23  
**專案狀態**: ✅ **核心功能完成，可立即使用於活動**  
**下次開發**: 修復線上活動頁面 HTML 更新問題  
**文檔位置**: `20260123_PROJECT_COMPACT.md`
