# Live Event Photography Constitution

## Core Principles

### I. Config-Driven, Zero Hardcode

所有可變參數 MUST 集中管理於 `config/config.json` 或 `config/event_settings.json`。嚴禁在程式碼中硬編碼路徑、遠端名稱、Bucket 名稱或活動專屬值。

- 所有 R2 相關設定（`R2_PATH_PREFIX`、`RCLONE_REMOTE`、`BUCKET_NAME`）MUST 從 config 讀取
- 新增設定項時 MUST 在 `DEFAULT_CONFIG` 中定義 fallback 值
- 存取 config 值 MUST 使用 `CONFIG.get("key", default)` 而非 `CONFIG["key"]`
- 前端需要的設定 MUST 透過 API 端點取得，不得寫死在 HTML/JS 中

**理由**: 本專案服務不同活動，每次活動的路徑、標題、設定都不同。硬編碼導致每次都要改多個檔案，已造成過多次遺漏事故。

### II. Consistent API Contract

所有 API 端點 MUST 遵循統一的回應格式：

**成功回應**:
```json
{"status": "success", "data": {...}}
```

**錯誤回應**:
```json
{"status": "error", "detail": "錯誤描述"}
```

- 成功操作 MUST 回傳 `{"status": "success"}` 加上操作結果
- 錯誤 MUST 使用 `HTTPException`，禁止混用 `JSONResponse(status_code=5xx)`
- List 類端點 MUST 回傳 `{"status": "success", "data": [...]}` 格式
- 所有端點 MUST 有 `try/except` 錯誤處理，不得讓未捕獲的例外洩漏到前端

**理由**: 目前 API 回應格式不一致（有的是 plain dict，有的用 JSONResponse），前端需要為每個端點寫不同的解析邏輯。

### III. Python Naming & Style

Python 程式碼 MUST 遵循以下命名規則：

- **函式/變數**: `snake_case`（如 `load_config_file`、`update_manifest`）
- **類別**: `PascalCase`（如 `ImageProcessor`、`PublishRequest`）
- **常數**: `UPPER_SNAKE_CASE`（如 `DEFAULT_CONFIG`、`EVENT_SETTINGS_FILE`）
- **私有方法**: `_snake_case`（如 `_apply_watermark`）
- **Pydantic Model**: `PascalCase`，欄位名 `snake_case`
- **Config JSON keys**: `snake_case`（如 `buffer_folder`、`jpeg_quality`）

日誌 MUST 使用 `logging` 模組（`logger.info/error/warning`），嚴禁在 production 程式碼中使用 `print()`。

**理由**: `sync_to_r2.py` 目前使用 `print()` 而非 `logger`，與 `server.py` 不一致。

### IV. Frontend Conventions

前端程式碼（`admin.html`、`index.html`）MUST 遵循：

- **JS 變數/函式**: `camelCase`（如 `fetchBuffer`、`currentFile`）
- **JS 常數**: `UPPER_SNAKE_CASE`（如 `MANIFEST_URL`）
- **DOM Element IDs**: `kebab-case`（如 `buffer-table-body`、`stats-modal`）
- **CSS 類名**: 優先使用 Tailwind utility classes；自訂 CSS 類名用 `kebab-case`
- **CSS 變數**: `--kebab-case`（如 `--bg-color`、`--accent-color`）
- **事件綁定**: 新功能 MUST 使用 `addEventListener`；禁止新增 inline `onclick`（現有的可逐步遷移）
- **API 呼叫**: MUST 使用 `async/await` + `fetch()`，MUST 有 `try/catch` 錯誤處理
- **使用者回饋**: 操作結果 MUST 透過 `showToast()` 通知，禁止使用 `alert()`

**理由**: 現有程式碼混用 inline onclick 和 addEventListener，造成維護困難。

### V. Documentation as Code

文件 MUST 與程式碼同步維護：

- 文件檔案命名 MUST 使用 `kebab-case.md`
- 有日期的文件 MUST 以 `YYYY-MM-DD-` 為前綴
- 文件 MUST 放在對應分類目錄：
  | 目錄 | 用途 |
  |------|------|
  | `docs/guides/` | 使用者操作指南 |
  | `docs/reference/` | 技術參考 |
  | `docs/dev/` | 開發者文件 |
  | `docs/dev/plans/` | 開發計劃（帶日期） |
  | `docs/dev/logs/` | 開發日誌（帶日期） |
  | `docs/archive/` | 歷史紀錄 |
- 新增或修改 API 端點時 MUST 同步更新 `docs/reference/project-status.md`
- 新增文件後 MUST 更新 `docs/README.md` 索引

**理由**: 專案曾有 19 個散亂狀態檔案，經 2026-02-11 整理後建立了統一結構，MUST 維持。

### VI. Single Source of Truth

每一類資訊 MUST 只有一個權威來源，禁止在多處維護相同資訊：

- **照片資料夾路徑**: 唯一來源是 `config/config.json`
- **活動設定**: 唯一來源是 `config/event_settings.json`
- **浮水印設定**: 唯一來源是 `config/config.json` 的 `processing.watermark`
- **已發布照片清單**: 唯一來源是 `photos_web/manifest.json`
- **R2 同步設定**: 唯一來源是 `config/config.json`（待實作，目前違反此原則）

當多個模組需要相同資訊時，MUST 統一從該來源讀取。禁止「在 server.py 定義一次、在 sync_to_r2.py 再定義一次」。

**理由**: `R2_PATH_PREFIX` 硬編碼在 4 個檔案中是此原則被違反的典型案例。

### VII. Graceful Degradation

系統 MUST 在以下異常情況下維持基本可用性：

- **External SSD 未連接**: MUST 回退到本地目錄，不得 crash
- **R2 sync 失敗**: MUST 記錄錯誤並在下次 cycle 重試，不得中斷
- **照片處理失敗**: MUST 記錄錯誤並跳過該張，不得影響其他照片
- **Config 檔案損壞/遺失**: MUST 使用 `DEFAULT_CONFIG` 回退
- **前端圖片載入失敗**: MUST 自動隱藏，不得顯示破圖

**理由**: 本系統用於現場活動，任何中斷都意味著即時照片無法發布。可靠性優先於完美性。

## Technology Stack

以下技術選型已確立，非必要不變更：

| 層級 | 技術 | 版本 |
|------|------|------|
| Backend Framework | FastAPI + Uvicorn | Python 3.10+ |
| Image Processing | Pillow (PIL) | Latest |
| Cloud Storage | Cloudflare R2 (S3-compatible) | - |
| Sync Tool | rclone | Latest |
| Static Hosting | Cloudflare Pages + Functions | - |
| Frontend CSS | Tailwind CSS (CDN) | v3+ |
| Frontend JS | Vanilla JavaScript | ES2020+ |

**禁止引入**:
- 前端框架（React/Vue/Angular）— 本專案是單頁管理界面，Vanilla JS 足夠
- Python ORM — 本專案不使用資料庫
- 套件打包工具（Webpack/Vite）— 前端透過 CDN 和 inline 即可

## Development Workflow

### 新功能開發流程

1. **P2 以上功能**: MUST 先建立 `specs/{feature}/spec.md` + `plan.md`，經確認後才開始實作
2. **P0/P1 修復**: 可直接修改，但 MUST 在 `docs/dev/logs/` 記錄變更
3. **所有變更**: MUST 更新 `docs/dev/changelog.md`

### 程式碼品質

- 新增函式 MUST 有 docstring（Python）或 JSDoc 註解
- API 端點 MUST 有 FastAPI 的 description 參數
- 共用邏輯 MUST 抽取為函式，禁止 copy-paste
- 前端超過 50 行的功能 SHOULD 抽取為獨立函式

### 測試

- 圖片處理相關修改 MUST 手動驗證（至少 1 張照片走完 publish → R2 sync → gallery 顯示）
- API 端點修改 MUST 驗證正常和錯誤兩個 case
- 前端修改 MUST 在 Chrome + Safari 兩個瀏覽器驗證

## Governance

- 本 Constitution 為專案最高準則，所有開發 MUST 遵守
- 如需修訂，MUST 在此文件中記錄變更原因與日期
- 新加入的 AI 助手或開發者 SHOULD 先閱讀本文件
- 與本 Constitution 衝突的現有程式碼 SHOULD 在修改該區域時順便修正（不需專門重構）

**Version**: 1.0.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-11
