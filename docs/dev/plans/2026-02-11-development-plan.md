# 開發計劃 — 2026-02-11

**建立日期**: 2026-02-11  
**專案版本**: v2.3+  
**專案狀態**: 核心功能 Production Ready，進入優化與擴充階段

---

## 專案現況摘要

### 已完成功能 (Feature Complete)

| 功能 | 完成度 | 備註 |
|------|--------|------|
| 核心工作流程 (Camera → Buffer → Admin → Publish → R2 → Gallery) | 100% | 穩定運作 |
| 照片編輯 (Exposure / Rotation / Straighten / Scale) | 100% | |
| R2 自動同步 (每 3 秒) | 100% | Safe mode |
| Admin UI 三欄佈局 + 快捷鍵 | 100% | |
| External SSD 支援 | 100% | 路徑可在 Admin 設定 |
| macOS 隱藏檔清理 | 100% | 多層防護 |
| Event Settings (標題/副標題/字型/Hero) | 100% | 支援即時更新 |
| Hero Banner 管理 API | 100% | 上傳/歷史庫/切換 |
| Sequential Filename 策略 | 100% | 防止覆蓋 |
| Cloudflare Pages Function (R2 Proxy) | 100% | |

### 部分完成功能

| 功能 | 完成度 | 缺少項目 |
|------|--------|----------|
| Watermark 浮水印 | 70% | 字型選擇、視覺化定位 |
| Cloudflare Deployment | 80% | 線上 HTML 更新問題 |
| Batch Publish | 60% | 僅支援統一 exposure，無獨立參數 |
| Hero Banner Admin UI | 85% | 部分按鈕點擊無反應、圖片庫讀取不全 |

---

## 待開發項目（按優先級排序）

### P0 — 緊急修復（影響正式活動使用）

#### 1. `R2_PATH_PREFIX` 動態化
- **現況**: `"2026-01-20"` 硬編碼在 4 個檔案中
  - `server.py` (line 866)
  - `sync_to_r2.py` (line 56)
  - `r2_manage.py` (line 22)
  - `scripts/fix_r2_manifest.py` (line 21)
- **風險**: 每次新活動需手動改多處，容易遺漏
- **方案**: 統一讀取 `config/config.json` 中的 `r2_path_prefix` 欄位
- **工作量**: 0.5 天

#### 2. Hero Banner UI Bugs 修復
- **現況**: 2026-02-06 更新後殘留的 JS 問題
  - 刪除/套用網址按鈕點擊無反應
  - 歷史圖片庫部分檔案未顯示
  - 模式切換時 JSON 欄位短暫失效
- **方案**: 檢查 `templates/admin.html` 中的事件綁定與 API 回傳處理
- **工作量**: 0.5 天

#### 3. 線上 HTML 更新確認
- **現況**: 本地 `index.html` 已修正，Cloudflare Pages 可能未部署最新版
- **排查步驟**:
  1. 確認 Cloudflare Dashboard → Pages → Deployments 狀態
  2. 無痕模式 + `?v=timestamp` 測試
  3. 驗證 Pages Build Output Directory 設定
- **工作量**: 0.5 天

### P1 — 高優先級（提升實用性）

#### 4. Batch Publish 獨立編輯參數
- **現況**: `/api/batch_publish` 所有照片共用同一個 `exposure`，不支援 `rotation`/`straighten`/`scale`
- **方案**:
  ```python
  # 新的 API Request Body
  class BatchPublishItem(BaseModel):
      filename: str
      exposure: float = 0.0
      rotation: int = 0
      straighten: float = 0.0
      scale: float = 1.0

  class BatchPublishRequest(BaseModel):
      items: List[BatchPublishItem]
  ```
- **涉及檔案**: `server.py`, `templates/admin.html`
- **工作量**: 1 天

#### 5. EXIF Metadata 保留
- **現況**: `process_image()` 中 `ImageOps.exif_transpose()` 後 EXIF 資訊遺失
- **影響**: 丟失拍攝時間、相機型號、GPS 等資訊
- **方案**: 使用 `piexif` 或 Pillow 原生 `img.getexif()` 回寫
- **涉及檔案**: `server.py` (`ImageProcessor.process_image()`)
- **工作量**: 0.5 天

#### 6. Admin UI 基礎認證
- **現況**: 完全無認證，任何人可透過 `localhost:8000` 操作
- **方案**: FastAPI HTTP Basic Auth 或 session-based password
- **涉及檔案**: `server.py`, `templates/admin.html`
- **工作量**: 1 天

### P2 — 中優先級（體驗優化）

#### 7. Mobile Admin UI 適配
- **現況**: 三欄佈局無 responsive design，手機無法操作
- **方案**: CSS Media Queries 改單欄/雙欄 + 觸控按鈕
- **涉及檔案**: `templates/admin.html`
- **工作量**: 2-3 天

#### 8. Watermark 進階選項
- **現況**: 基礎功能可用（文字/圖片、位置、透明度）
- **缺少**: 字型選擇介面、視覺化拖拽定位、即時預覽
- **工作量**: 1-2 天

#### 9. R2 Manifest Cache 優化
- **現況**: 前端用時間戳繞過 cache
- **方案**: 改用版本號 + Cloudflare Edge Cache API
- **工作量**: 0.5 天

### P3 — 低優先級（未來增強）

| # | 項目 | 說明 |
|---|------|------|
| 10 | 縮圖生成 + Lazy Loading | 優化前端載入速度 |
| 11 | 發布統計 / 時間軸視覺化 | 活動數據面板 |
| 12 | 自動備份 + R2 版本控制 | 資料安全 |
| 13 | 代碼重構 | 拆分 `ImageProcessor` 為獨立模組、引入 `.env` |
| 14 | R2 上傳重試機制 + API Rate Limit | 穩定性 |
| 15 | 照片處理並行化 | 多線程/異步提升效能 |

---

## 技術債務

| 項目 | 說明 | 影響程度 |
|------|------|----------|
| `R2_PATH_PREFIX` 硬編碼 | 散布在 4 個檔案 | 高 — 每次活動必須改 |
| 無單元測試 | 核心邏輯零測試覆蓋 | 中 |
| `server.py` 過大 | 1500+ 行，職責混合 | 中 |
| `config.json` 路徑混用 | `watch_folder` vs `buffer_folder` 命名不一致 | 低 |

---

## 建議執行時程

### 第 1 週：修復基礎問題 (P0)
- [ ] `R2_PATH_PREFIX` 動態化 — 統一 4 個檔案讀取 config
- [ ] Hero Banner UI Bugs — JS 事件綁定修復
- [ ] Cloudflare Pages 部署確認

### 第 2 週：增強核心功能 (P1)
- [ ] Batch Publish 獨立參數重寫
- [ ] EXIF Metadata 保留實作
- [ ] Admin Basic Auth 加入

### 第 3 週：體驗優化 (P2)
- [ ] Mobile Admin UI responsive 適配
- [ ] Watermark 進階功能

### 第 4 週：穩定化
- [ ] R2 Manifest 版本化
- [ ] 端到端測試
- [ ] 文件更新

---

## 文件命名規範（本次整理確立）

本次文件整理統一了 `docs/` 的命名與分類規則：

### 命名規則
- **一律 `kebab-case.md`**（小寫、連字號分隔）
- 有日期的檔案以 `YYYY-MM-DD-` 為前綴
- 範例：`2026-02-11-development-plan.md`、`getting-started.md`

### 目錄分類
| 目錄 | 用途 | 範例 |
|------|------|------|
| `docs/guides/` | 使用者操作指南 | `getting-started.md`, `deployment.md` |
| `docs/reference/` | 技術參考文件 | `architecture.md`, `project-status.md` |
| `docs/dev/` | 開發者文件 | `changelog.md`, `roadmap.md` |
| `docs/dev/plans/` | 開發計劃（帶日期） | `2026-02-11-development-plan.md` |
| `docs/dev/logs/` | 開發日誌（帶日期） | `2026-02-06-update.md` |
| `docs/archive/` | 歷史紀錄 | 已解決問題的筆記、舊版狀態報告 |

---

**建立者**: Development Session  
**最後更新**: 2026-02-11
