# 快速入門指南

本指南幫助你在 5 分鐘內開始使用 Live Event Photography。

## 📋 前置需求

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **pip 套件**
   ```bash
   pip install -r requirements.txt
   ```

3. **rclone** (用於 R2 同步)
   ```bash
   brew install rclone
   ```

## 🚀 啟動系統

### 方式一：一鍵啟動（推薦）

```bash
./scripts/start_event.sh
```

### 方式二：雙擊 App

雙擊根目錄的 `Launch Live Event Photo.command`

### 方式三：手動啟動

```bash
# Terminal 1
python3 server.py

# Terminal 2
python3 sync_to_r2.py
```

## 🌐 開啟介面

- **管理後台**: http://localhost:8000
- **活動頁面**: http://localhost:8000/gallery

## 📸 基本工作流程

1. **相機照片** → 拷貝到 `photos_buffer/`
2. **Admin 後台** → 選擇照片 → 調整參數 → 按 Enter 發布
3. **自動同步** → 照片會自動同步到 Cloudflare R2
4. **觀眾瀏覽** → 透過活動頁面即時看到新照片

## ⌨️ 常用快捷鍵

| 按鍵 | 功能 |
|------|------|
| `Space` / `→` | 下一張照片 |
| `Enter` | 發布照片 |
| `Delete` | 封存（移到 trash） |
| `R` | 旋轉 90° |

## ⚙️ 設定

點擊 Admin 後台右上角的 ⚙️ 按鈕：

1. **活動設定** — 標題、副標題、背景圖
2. **浮水印設定** — 開關、位置、透明度
3. **資料夾設定** — 設定外接 SSD 路徑

## 📁 資料夾說明

| 資料夾 | 用途 |
|-------|------|
| `photos_buffer/` | 相機原圖輸入 |
| `photos_web/` | 已發布（同步到 R2） |
| `photos_trash/` | 已刪除 |
| `photos_archive/` | 封存 |

## 🔧 問題排解

遇到問題？請查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**下一步**: 閱讀 [OPERATION_MANUAL.md](OPERATION_MANUAL.md) 了解完整操作
