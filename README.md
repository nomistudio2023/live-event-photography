# Live Event Photography

**即時活動攝影發布系統** | Real-time Photo Publishing System for Live Events

[![Version](https://img.shields.io/badge/version-v2.3+-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)]()

---

## 📸 專案簡介

Live Event Photography 是一個專為活動攝影師設計的即時照片發布系統。照片從相機拍攝到網頁顯示只需不到 1 分鐘，支援 2500+ 張照片和 500+ 並發觀看者。

### ✨ 主要功能

- ⚡ **即時發布** — 從拍攝到網頁顯示 < 1 分鐘
- 🎨 **照片編輯** — 曝光、旋轉、水平校正、縮放
- 💧 **浮水印** — 支援圖片/文字浮水印
- ☁️ **雲端同步** — 自動同步到 Cloudflare R2
- 📱 **響應式設計** — 支援手機/平板/電腦瀏覽
- 💾 **外接 SSD** — 支援大容量外接儲存

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 一鍵啟動

```bash
./scripts/start_event.sh
```

或手動啟動：

```bash
# Terminal 1 - 後端服務
python3 server.py

# Terminal 2 - R2 同步
python3 sync_to_r2.py
```

### 3. 開啟管理後台

瀏覽 `http://localhost:8000`

---

## 📁 專案結構

```
live-event-photography/
├── 📄 核心程式
│   ├── server.py          # FastAPI 後端服務器
│   ├── sync_to_r2.py      # R2 自動同步腳本
│   └── r2_manage.py       # R2 管理工具
│
├── 🎨 前端
│   ├── index.html         # 活動展示頁面
│   └── templates/
│       └── admin.html     # 管理後台
│
├── ⚙️ 設定
│   └── config/
│       ├── config.json           # 系統設定
│       └── event_settings.json   # 活動頁面設定
│
├── 📜 腳本
│   └── scripts/
│       ├── start_event.sh        # 一鍵啟動
│       ├── cleanup_hidden_files.py
│       └── ...
│
├── 📚 文檔
│   └── docs/
│       ├── ARCHITECTURE.md       # 系統架構
│       ├── TROUBLESHOOTING.md   # 疑難排解
│       └── archive/              # 歷史記錄
│
└── 📁 資料夾 (可設定為外接 SSD)
    ├── photos_buffer/     # 相機輸入
    ├── photos_web/        # 已發布
    ├── photos_trash/      # 已刪除
    └── photos_archive/    # 封存
```

---

## 🔧 設定

### 系統設定 (`config/config.json`)

```json
{
  "buffer_folder": "./photos_buffer",
  "web_folder": "./photos_web",
  "max_size": 1600,
  "jpeg_quality": 85,
  "processing": {
    "sharpen": true,
    "watermark": {
      "enabled": true,
      "position": "bottom-right"
    }
  }
}
```

### 活動設定 (`config/event_settings.json`)

透過管理後台 (⚙️ 設定按鈕) 進行設定：
- 活動標題/副標題
- 背景圖片
- 字型設定

---

## 🌐 雲端部署

本系統使用 **Cloudflare R2 + Pages** 進行雲端部署：

1. R2 儲存照片
2. Pages Function 代理 R2 存取
3. 自動每 3 秒同步新照片

詳見 [docs/R2_SETUP_GUIDE.md](docs/R2_SETUP_GUIDE.md)

---

## ⌨️ 快捷鍵

| 按鍵 | 功能 |
|------|------|
| `Space` / `→` | 下一張 |
| `Enter` | 發布 |
| `Delete` | 封存 |
| `R` | 旋轉 90° |
| `U` | 取消發布 |

---

## 📖 更多文檔

- [系統架構](docs/ARCHITECTURE.md)
- [疑難排解](docs/TROUBLESHOOTING.md)
- [操作手冊](docs/OPERATION_MANUAL.md)
- [部署指南](docs/DEPLOYMENT_GUIDE.md)

---

## 📜 版本歷史

詳見 [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

**最後更新**: 2026-02-06
