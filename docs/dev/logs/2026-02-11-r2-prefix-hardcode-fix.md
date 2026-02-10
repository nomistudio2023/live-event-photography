# 2026-02-11 開發日誌：R2 Path Prefix 硬編碼修復

## 📌 摘要

修復 `index.html` 中 R2 path prefix `2026-01-20` 的硬編碼問題（P0），並連帶改善 bootstrap 失敗時的用戶體驗。此修復涉及 4 個檔案的連動改動，建立了 config-driven 的動態 URL 機制，符合 Constitution Principle I（Config-Driven, Zero Hardcode）與 Principle VII（Graceful Degradation）。

---

## 1. Bug 1：R2 Path Prefix 硬編碼

### 問題描述

`index.html` 第 493-495 行硬編碼了 `2026-01-20` 三次：

```javascript
const MANIFEST_URL = isLocal ? 'photos_web/manifest.json' : '/photo/2026-01-20/manifest.json';
const IMAGE_BASE_URL = isLocal ? 'photos_web/' : '/photo/2026-01-20/';
const EVENT_SETTINGS_URL = isLocal ? '/api/event-settings' : '/photo/2026-01-20/event_settings.json';
```

**違反**：Constitution Principle I — 所有 R2 相關設定應從 config 讀取，不應硬編碼在前端程式碼中。每次新活動需手動改 code 而非改 config。

### 根因分析

前端（靜態 HTML 部署於 Cloudflare Pages）無法直接讀取後端的 `config.json`。因此需要一個 bootstrap 機制：前端先從一個**固定已知路徑**取得設定，再從設定中取得動態 prefix。

存在 chicken-and-egg 問題：要讀 `event_settings.json` 就需要知道 prefix，但 prefix 就在 `event_settings.json` 裡。

### 解決方案

建立四層連動修改，以 `config/config.json` 為 Single Source of Truth：

#### 1.1 `config/config.json` — 新增 `r2_path_prefix`

```json
{
  "r2_path_prefix": "2026-01-20",
  ...
}
```

#### 1.2 `server.py` — 注入 `r2_path_prefix` 到 event-settings

- `GET /api/event-settings` 回應自動注入 `CONFIG["r2_path_prefix"]`
- `save_event_settings()` mirror 到 web folder 時也注入，確保 R2 sync 後前端可取得

#### 1.3 `sync_to_r2.py` — 從 config 讀取 + 雙路徑同步

- `load_config()` 改為回傳 `(web_folder, r2_path_prefix)` tuple
- `R2_PATH_PREFIX` 不再硬編碼，從 config.json 讀取
- `sync_static_files()` 同步 `event_settings.json` 時：
  - 注入 `r2_path_prefix` 欄位
  - 同步到 `{R2_PATH_PREFIX}/event_settings.json`（原路徑，向後相容）
  - **額外**同步到 R2 root 的 `event_settings.json`（解決 chicken-and-egg）

#### 1.4 `index.html` — 動態 bootstrap 機制

**Before（硬編碼）**：
```javascript
const MANIFEST_URL = isLocal ? '...' : '/photo/2026-01-20/manifest.json';
```

**After（動態）**：
```javascript
let MANIFEST_URL = isLocal ? 'photos_web/manifest.json' : '';
// Online: 從 R2 root 固定路徑 /photo/event_settings.json bootstrap
// → 取得 r2_path_prefix → 動態建構所有 URL
```

初始化流程：
1. **Local 模式**：URL 直接設為本地路徑（行為不變）
2. **Online 模式**：
   - `initApp()` → `bootstrapOnline()` fetch `/photo/event_settings.json`（R2 root）
   - 取出 `r2_path_prefix`，動態建構 `MANIFEST_URL`、`IMAGE_BASE_URL`、`EVENT_SETTINGS_URL`
   - 套用 event settings → 啟動 polling

### 驗證

- `index.html` 中不再包含任何 `2026-01-20` 字串
- 換活動只需修改 `config/config.json` 的 `r2_path_prefix` 值，零程式碼修改

---

## 2. Bug 2：Bootstrap 失敗時用戶看到空白頁

### 問題描述

Bug 1 修復後的 `initApp()` 引入了新的邊界問題：當 online bootstrap 失敗（網路錯誤、404、`r2_path_prefix` 缺失）時：

- 只有 `console.error` 輸出（用戶不可見）
- `loadEventSettings()` 和 `fetchPhotos()` 因空 URL guard clause 直接 `return`
- Polling interval 持續觸發但全部空轉
- **用戶看到完全空白頁面，無任何提示**

**違反**：Constitution Principle VII — 系統應在異常情況下維持基本可用性。

### 解決方案

#### 2.1 `bootstrapOnline()` — 獨立函式，回傳 boolean

將 bootstrap 邏輯抽取為獨立函式，回傳 `true/false` 明確表示成功或失敗，支援重試呼叫。

#### 2.2 `showBootstrapError()` — 用戶可見的錯誤畫面

復用 `empty-state` CSS 樣式，以黃/紅漸變標題區分於正常的「活動即將開始」空狀態：

- ⚠️ 圖標（無 bounce 動畫）
- 「無法載入相簿設定」標題
- 「頁面將在幾秒後自動重試…」副標題

#### 2.3 Exponential Backoff 重試

```
重試間隔：2s → 4s → 8s → 15s → 30s（共 5 次）
```

- Bootstrap 成功 → 清除錯誤畫面 → `startPolling()` 啟動正常 polling
- 全部重試失敗 → 更新副標題為「請檢查網路連線後重新整理頁面」
- 仍持續每 30 秒嘗試一次（服務恢復時自動 recovery）

#### 2.4 `startPolling()` — 封裝 polling 啟動

只在 bootstrap 成功後才呼叫，杜絕空 URL 空轉浪費。

---

## 修改檔案清單

| 檔案 | 改動類型 | 說明 |
|------|---------|------|
| `config/config.json` | 新增欄位 | `r2_path_prefix: "2026-01-20"` |
| `server.py` | 修改 | `get_event_settings()` 注入 prefix；`save_event_settings()` mirror 時注入 |
| `sync_to_r2.py` | 修改 | `load_config()` 讀取 prefix；`sync_static_files()` 雙路徑同步 + 注入 |
| `index.html` | 重構 | 移除硬編碼；新增 bootstrap 機制、錯誤畫面、exponential backoff 重試 |

---

## 對應開發計劃項目

- ✅ P0-001: `R2_PATH_PREFIX` 硬編碼（`index.html` 部分已修復）
- 📝 備註：`server.py`、`sync_to_r2.py` 中的其他 `R2_PATH_PREFIX` 硬編碼已在本次一併修正（`sync_to_r2.py` 改從 config 讀取）
