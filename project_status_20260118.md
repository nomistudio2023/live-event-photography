# Live Event Photography Project - 進度報告 (2026-01-18)

## 📅 專案狀態摘要
- **本地生產端 (Local Production)**: ✅ 已完成且功能完整
- **雲端同步端 (Cloud Uplink)**: ⏳ 待啟動 (Next Step)
- **整體架構**: 多步驟處理流水線 (Pipeline) 架構，從相機監控到前端展示。

---

## 🛠️ 目前功能規格 (Spec v3.1)

### 1. 後端影像處理引擎 ()
- **監控機制**: 使用 `watchdog` 實時監聽 `photos_original` 資料夾。
- **影像最佳化 (Optimization)**:
  - **智慧銳利化**: Unsharp Mask 濾鏡補償縮圖細節。
  - **漸進式載入**: 存檔為 Progressive JPEG。
  - **智慧轉向**: 自動修正 EXIF Orientation。
  - **縮圖策略**: 長邊壓縮至 1600px (可於 config 設定)。
- **Branding 模組**:
  - 支援 **浮水印 (Watermark)** 與 **邊框 (Frame)** 疊加。
  - 具備自動裁切 (Cover) 或完整縮放 (Contain) 模式。
  - 目前狀態: 浮水印功能已啟用，測試素材 `assets/watermark.png` 已生成。
- **清單生成**: 自動維護 `photos_web/manifest.json`，供前端讀取。

### 2. 前端展示介面 ()
- **視覺風格**: 現代化黑色玻璃質感 (Dark Glassmorphism)。
- **版面配置 (Responsive Layout)**:
  - **Masonry 瀑布流**: 
    - Desktop: 4 欄
    - Tablet/Horizontal Mobile: 3 欄
    - Vertical Mobile: 3 欄 (CSS 變數可調)
  - **Live Banner**: 置頂展示最新上傳的照片，具備淡入動畫。
- **燈箱體驗 (Lightbox v3.1)**:
  - **手機操作優化 (IG Stories 風格)**: 
    - 點擊左側 30% -> 上一張
    - 點擊右側 30% -> 下一張
    - 支援 Touch Swipe (左右滑動) 手勢。
    - 手機版隱藏實體按鈕，追求照片最大化展示。
  - **桌面操作**: 保留左右懸浮箭頭按鈕 + 鍵盤左右鍵導航。
  - **下載功能**: 內建「下載原圖」按鈕。

### 3. 設定管理 ()
- 集中管理所有參數：輸入/輸出路徑、壓縮品質、浮水印開關/位置/透明度。

---

## �� 檔案結構
```text
live-event-photography/
├── auto_compress.py       # (舊版備份) V1 基礎腳本
├── auto_compress_v2.py    # (核心) V2 進階影像處理引擎
├── config.json            # (設定) 系統參數設定檔
├── generate_watermark.py  # (工具) 產生測試用浮水印
├── index.html             # (核心) V3.1 前端展示頁面
├── index_v2.html          # (舊版備份) V2 前端頁面
├── photos_original/       # [Input] 相機傳輸監控資料夾
├── photos_web/            # [Output] 網頁用素材 (含 manifest.json)
└── assets/                # [Input] 浮水印、邊框素材
    └── watermark.png
```

---

## 🚀 下一步計畫 (Next Steps)
1.  **雲端同步 (The Uplink)**:
    - 設定 `rclone` 連接 Cloudflare R2 或 AWS S3。
    - 建立背景同步指令，將 `photos_web` 實時鏡像至 CDN。
2.  **進階監控 (Dashboard)**:
    - (選用) 加入本地流量顯示或簡單的狀態儀表板。
3.  **上線部署 (Deployment)**:
    - 實際將 `index.html` 部署至靜態託管服務 (如 Cloudflare Pages 或 GitHub Pages)。

