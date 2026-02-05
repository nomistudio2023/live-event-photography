# Live Event Photography Project - 進度報告 (2026-01-20)

## 📅 專案狀態摘要
- **本地生產端 (Local Command Center)**: 🚀 v2.3 已完成，進入「人機協作 (Human-in-the-Loop)」模式。
- **前端展示端 (Live Gallery)**: ✅ 已完成 Grid Layout 與手機版優化。
- **整體架構**: 轉型為「先審後發 (Cull-then-Publish)」流程，確保照片品質。

---

## 🛠️ 目前功能規格 (Command Center v2.3)

### 1. 後端影像處理引擎 (`server.py`)
- **FastAPI 架構**: 取代單純的 Loop 腳本，提供完整的 RESTful API。
- **API Endpoints**:
    - `/api/buffer`: 讀取 Inbox 資料與歷史紀錄。
    - `/api/live`: 讀取已發布資料與歷史紀錄。
    - `/api/publish`: 處理照片 (轉正、銳化、浮水印、亮度調整) 並發布。
    - `/api/unpublish`: 下架照片 (刪除 Web 檔案，保留原始檔)。
    - `/api/history`: (內部邏輯) 透過 `history.json` 記錄每張照片的 P (Publish) / R (Retract) 次數。
- **曝光補償**: 支援在發布前進行亮度調整 (Exposure Compensation)。

### 2. 本地控制台 (`templates/admin.html`)
- **三欄式彈性佈局**:
    - **左欄 (Inbox & History)**: 上半部顯示待處理照片，下半部顯示已發布歷史。
    - **中欄 (Workspace)**: 大圖預覽、亮度滑桿、Park (Archive) / Publish (Ready) 按鈕。
    - **右欄 (Live Feed)**: 垂直單欄顯示已上線照片，強制 **4:3 比例**，含「一鍵下架」與「檔名顯示」功能。
- **互動優化**: 
    - 支援滑鼠拖曳調整欄寬。
    - 支援批次選取發布。
    - 右上角 "Open Gallery" 快速傳送門。

### 3. 前端展示頁面 (`index.html`)
- **Layout 升級**: 棄用 Masonry (瀑布流)，改用 **CSS Grid**，確保照片由左至右、由上而下的閱讀順序。
- **響應式設計**:
    - Desktop: 3 欄
    - Tablet: 2 欄
    - Mobile (<400px): **1 欄** (單欄大圖模式)。
- **資料源**: 持續讀取 `photos_web` 資料夾。

---

## 🐛 已知問題 (Known Issues)
1. **Inbox 標籤顯示異常**: 
   - 儘管後端已回傳 `published_count` 與 `unpublished_count`，目前 Inbox 列表中的檔名旁尚未正確顯示 `P:1` 或 `R:1` 標籤。
   - **狀態**: 已確認，暫緩修復 (Backlog)。

---

## 📂 檔案結構更新
```text
live-event-photography/
├── server.py              # [Core] FastAPI 後端伺服器 (整合 ImageProcessor)
├── history.json           # [Data] 發布/收回次數紀錄庫
├── templates/
│   └── admin.html         # [UI] 攝影師控制台 (Command Center)
├── index.html             # [Frontend] 賓客觀看頁面
├── photos_buffer/         # [Input] 相機拍攝進件 (待審核)
├── photos_web/            # [Output] 已發布 (Live)
├── photos_archive/        # [Storage] 已封存 (Parked)
├── photos_trash/          # [Trash] 已刪除
└── assets/
    └── watermark.png
```

## 🚀 下一步 (Next Steps)
1. **修復 Inbox 標籤**: 解決前端未能正確渲染歷史次數 Badge 的問題。
2. **部署準備**: 設定雲端同步機制 (rclone) 連接最終 CDN。
