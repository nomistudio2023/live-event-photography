# Live Event Photography 操作手冊
**建立日期**: 2026-01-22
**系統版本**: 2.0 (R2 Storage)

---

## 📋 活動前準備（活動前一天）

### 1. 確認系統環境
```bash
# 確認 Python 已安裝
python3 --version

# 確認 rclone 已安裝
rclone --version

# 測試 R2 連線
rclone lsf r2livegallery:nomilivegallery/
```

### 2. 設定活動日期路徑
編輯以下兩個檔案，更新 `R2_PATH_PREFIX` 為活動日期：

**sync_to_r2.py** (第 30 行)
```python
R2_PATH_PREFIX = "2026-01-20"  # 改為實際活動日期
```

**r2_manage.py** (第 22 行)
```python
R2_PATH_PREFIX = "2026-01-20"  # 改為實際活動日期
```

### 3. 更新網站 manifest 路徑
編輯 GitHub 專案的 `index.html`：
```javascript
const MANIFEST_URL = '/photo/2026-01-20/manifest.json';  // 改為活動日期
const IMAGE_BASE_URL = '/photo/2026-01-20/';             // 改為活動日期
```

### 4. 清空本地照片資料夾
```bash
cd /Users/nomisas/.gemini/antigravity/scratch/live-event-photography
rm -rf photos_buffer/*
rm -rf photos_web/*
```

---

## 🚀 活動當天啟動流程

### 步驟 1：開啟終端機
```bash
cd /Users/nomisas/.gemini/antigravity/scratch/live-event-photography
```

### 步驟 2：一鍵啟動系統
```bash
./start_event.sh
```

**預期輸出：**
```
================================================
🎬 Live Event Photography - 活動模式啟動
================================================

📂 工作目錄: /Users/nomisas/.gemini/antigravity/scratch/live-event-photography

🖥️  啟動 Admin 後台...
   PID: XXXXX
   URL: http://localhost:8000

☁️  啟動 R2 同步腳本...

==================================================
🚀 R2 自動同步腳本 - Live Event Photography
==================================================
📂 監控資料夾: .../photos_web
☁️  R2 路徑: r2livegallery:nomilivegallery/2026-01-20/
⏱️  檢查間隔: 3 秒
--------------------------------------------------
按 Ctrl+C 停止

📸 本地照片: 0 張
☁️  R2 照片: 0 張

🔍 開始監控變化...
```

### 步驟 3：開啟 Admin 後台
瀏覽器開啟：**http://localhost:8000**

---

## 📸 活動中操作流程

### 上傳照片
1. 開啟 Admin 後台 (http://localhost:8000)
2. 點擊「選擇檔案」或拖放照片
3. 照片自動壓縮處理
4. 點擊「發布」按鈕
5. 同步腳本自動上傳到 R2
6. 終端機顯示：
   ```
   [HH:MM:SS] 📥 新增 1 張照片
      ✅ 已上傳: photo_name.jpg
      📋 Manifest 已更新 (R2: XX 張)
   ```

### 取消發布照片
1. 在 Admin 後台找到要移除的照片
2. 點擊「取消發布」
3. 同步腳本偵測變化（安全模式下 R2 照片保留）
4. 如需從 R2 刪除，使用管理工具：
   ```bash
   python3 r2_manage.py delete 照片名.jpg
   ```

### 批次刪除照片
```bash
python3 r2_manage.py delete-multi
```
依照提示選擇要刪除的照片編號。

---

## 🔧 活動中常用命令

### 查看 R2 照片列表
```bash
python3 r2_manage.py list
```

### 修復照片排序（新照片應在最前）
```bash
python3 r2_manage.py refresh
```

### 查看同步狀態
觀察終端機中 sync_to_r2.py 的輸出訊息。

---

## 🛑 活動結束流程

### 步驟 1：停止同步腳本
在執行 sync_to_r2.py 的終端機按 `Ctrl+C`

**預期輸出：**
```
👋 同步腳本已停止

🛑 正在關閉 Admin 後台 (PID: XXXXX)...
👋 所有服務已停止
```

### 步驟 2：最終確認
```bash
# 確認所有照片都在 R2
python3 r2_manage.py list

# 確認網站顯示正常
# 開啟活動頁面檢查
```

### 步驟 3：備份（可選）
```bash
# 備份本地照片
cp -r photos_web ~/Desktop/活動照片備份_$(date +%Y%m%d)
```

---

## ⚠️ 故障排除

### 問題：照片未出現在網站

**檢查步驟：**
```bash
# 1. 確認同步腳本執行中
# 查看終端機是否有 "🔍 開始監控變化..." 訊息

# 2. 確認照片已在 R2
python3 r2_manage.py list

# 3. 重新整理 manifest
python3 r2_manage.py refresh

# 4. 清除瀏覽器快取，重新載入網頁
```

### 問題：新照片出現在底部而非頂部

**解決方法：**
```bash
python3 r2_manage.py refresh
```

### 問題：同步腳本連線失敗

**檢查步驟：**
```bash
# 測試 rclone 連線
rclone lsf r2livegallery:nomilivegallery/

# 如果失敗，檢查網路連線
ping cloudflare.com
```

### 問題：Admin 後台無法開啟

**解決方法：**
```bash
# 手動啟動 server
python3 server.py

# 如果連接埠被占用
lsof -i :8000
kill -9 <PID>
python3 server.py
```

---

## 📱 活動頁面 QR Code

活動頁面網址：
```
https://live-event-photography.pages.dev
```

建議活動前製作 QR Code 供現場掃描。

---

## 📞 緊急聯絡

如遇無法解決的問題：
1. 記錄錯誤訊息截圖
2. 記錄操作步驟
3. 聯繫技術支援

---

## ✅ 操作檢查清單

### 活動前一天
- [ ] 確認系統環境（Python、rclone）
- [ ] 更新活動日期路徑
- [ ] 清空本地照片資料夾
- [ ] 測試 R2 連線
- [ ] 準備 QR Code

### 活動當天開場前
- [ ] 執行 `./start_event.sh`
- [ ] 確認 Admin 後台可開啟
- [ ] 確認同步腳本運作中
- [ ] 測試上傳一張照片
- [ ] 確認網站顯示正常

### 活動結束後
- [ ] 按 Ctrl+C 停止系統
- [ ] 執行 `python3 r2_manage.py list` 確認照片數量
- [ ] 備份本地照片（可選）

---

**文件建立**: 2026-01-22
**最後更新**: 2026-01-22
