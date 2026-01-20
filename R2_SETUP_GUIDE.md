# Cloudflare R2 + rclone 設定指南

## 📋 設定概覽
- **Bucket 名稱**: nomilivegallery
- **存放結構**: 按日期或活動分資料夾 (如 `2026-01-20/`, `event-2026-01/`)
- **上傳方式**: rclone 自動化同步

---

## 🔧 Step 1: 在 Cloudflare 建立 R2 Bucket

### 1.1 訪問 Cloudflare Dashboard
- 進入 https://dash.cloudflare.com
- 左側菜單選 **「R2」**（在「Storage」底下）

### 1.2 建立新 Bucket
1. 點擊藍色 **「Create bucket」** 按鈕
2. 填入以下資訊：
   ```
   Bucket name: nomilivegallery
   Location: 自動 (WNAM - US West)
   ```
3. 點擊 **「Create bucket」**

### 1.3 記錄 Bucket 信息
建立成功後，記下：
- **Bucket 名稱**: `nomilivegallery`
- **R2 API URL**: 如 `https://nomi-event-live-gallery.r2.cf.com`


---

## 🔑 Step 2: 配置 R2 API Token

### 2.1 建立 API Token
1. 在 Cloudflare Dashboard，點擊右上角 **「Account」** 或 **「Profile」**
2. 選 **「Account」** → **「API Tokens」**
3. 或直接訪問 https://dash.cloudflare.com/profile/api-tokens

### 2.2 建立新 Token
1. 點擊 **「Create Token」**
2. 選擇「Custom token」的 **「Get started」**
3. 填入以下設定：
   ```
   Token name: rclone-r2-sync
   Permissions:
     - Account > R2 > All buckets (Edit)

   Account Resources:
     - Include > All accounts
   ```
4. **不需要設 TTL**（留空表示永久）
5. 點擊 **「Continue to summary」** → **「Create Token」**

### 2.3 複製並保存 Token
**重要！此時會顯示 Token，之後無法再看到，請務必複製並保存**

格式類似：
```
c-xxxxxxxxxxx_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 💻 Step 3: 在本地安裝 rclone

### 3.1 檢查是否已安裝
```bash
rclone version
```

如果已安裝，跳至 Step 4。

### 3.2 安裝 rclone（Mac）
```bash
# 用 Homebrew 安裝
brew install rclone

# 驗證安裝
rclone version
```

### 3.3 安裝 rclone（Windows/Linux）
訪問 https://rclone.org/downloads/ 下載安裝

---

## 🔐 Step 4: 配置 rclone 遠端儲存

### 4.1 開始互動式配置
```bash
rclone config
```

### 4.2 選擇「新增遠端」
出現提示時：
```
n/s/q> n
name> r2-live-gallery
```

### 4.3 選擇 Storage Type
```
Type of storage> 19  (或搜尋 "s3" 找到 Amazon S3)
```

### 4.4 選擇 S3 Provider
```
Choose your S3 provider> 5  (或搜尋 "Cloudflare R2")
```

### 4.5 填入 S3 認證信息
```
Access Key ID> [你的 API Token]
Secret Access Key> [再次輸入 API Token]
Region> auto
Endpoint> https://nomi-event-live-gallery.r2.cf.com
```

**重要：**
- Access Key 和 Secret Key 都填入同一個 Token
- Endpoint 就是你的 R2 Bucket URL

### 4.6 完成配置
```
Edit advanced config?> n
Save this remote?> y
```

---

## 📂 Step 5: 測試上傳（單個照片）

### 5.1 準備測試照片
```bash
# 創建測試目錄結構
mkdir -p /Users/nomisas/Documents/r2-test/2026-01-20
cp /Users/nomisas/.gemini/antigravity/scratch/live-event-photography/photos_web/15D_7030.jpg /Users/nomisas/Documents/r2-test/2026-01-20/
```

### 5.2 上傳測試照片
```bash
rclone copy /Users/nomisas/Documents/r2-test/2026-01-20/ r2-live-gallery:2026-01-20/
```

### 5.3 驗證上傳成功
```bash
rclone ls r2-live-gallery:
```

應該看到：
```
        12345 2026-01-20/15D_7030.jpg
```

### 5.4 驗證 URL 可訪問
訪問：
```
https://nomi-event-live-gallery.r2.cf.com/2026-01-20/15D_7030.jpg
```

應該能在瀏覽器中看到照片。

---

## 🚀 Step 6: 完整同步所有照片

### 6.1 同步 photos_web 目錄（保留目錄結構）

**選項 A：按日期分類上傳**
```bash
# 假設照片分不同日期，建議先在本地組織好
# 例如：
# photos_web/
# ├── 2026-01-20/
# │   ├── 15D_7030.jpg
# │   ├── 15D_7049.jpg
# │   └── ...
# └── 2026-01-21/
#     ├── IMG_2678.jpg
#     └── ...

# 然後同步（保留資料夾結構）
rclone sync /Users/nomisas/.gemini/antigravity/scratch/live-event-photography/photos_web/ r2-live-gallery:photos/
```

**選項 B：同步所有照片到單一資料夾**
```bash
rclone sync /Users/nomisas/.gemini/antigravity/scratch/live-event-photography/photos_web/ r2-live-gallery:all-photos/
```

### 6.2 監控同步進度
```bash
# 添加 -v 參數查看詳細進度
rclone sync -v /Users/nomisas/.gemini/antigravity/scratch/live-event-photography/photos_web/ r2-live-gallery:photos/

# 添加 --dry-run 進行測試（不真正上傳）
rclone sync --dry-run /Users/nomisas/.gemini/antigravity/scratch/live-event-photography/photos_web/ r2-live-gallery:photos/
```

---

## 📝 Step 7: 更新 manifest.json

### 7.1 生成新的 manifest.json
你需要修改 `manifest.json` 中的 URL 從：
```json
["15D_7030.jpg", "15D_7049.jpg", ...]
```

改為：
```json
["photos/2026-01-20/15D_7030.jpg", "photos/2026-01-20/15D_7049.jpg", ...]
```

或者（如果上傳到 all-photos）：
```json
["all-photos/15D_7030.jpg", "all-photos/15D_7049.jpg", ...]
```

### 7.2 在 index.html 修改 IMAGE_BASE_URL
```javascript
// 修改從：
const IMAGE_BASE_URL = 'photos_web/';

// 改為：
const IMAGE_BASE_URL = 'https://nomi-event-live-gallery.r2.cf.com/photos/';
```

---

## 🔄 Step 8: 設定自動同步腳本（可選）

### 8.1 建立 bash 腳本自動同步
```bash
# 建立檔案 ~/sync-photos-r2.sh
cat > ~/sync-photos-r2.sh << 'EOF'
#!/bin/bash
# 自動同步照片到 R2

SOURCE_DIR="/Users/nomisas/.gemini/antigravity/scratch/live-event-photography/photos_web"
BUCKET="r2-live-gallery"
REMOTE_PATH="photos/"

echo "開始同步照片到 R2..."
rclone sync "$SOURCE_DIR" "$BUCKET:$REMOTE_PATH" -v --log-file=/tmp/rclone-sync.log

echo "同步完成！"
echo "日誌位置: /tmp/rclone-sync.log"
EOF

chmod +x ~/sync-photos-r2.sh
```

### 8.2 手動執行
```bash
~/sync-photos-r2.sh
```

### 8.3 自動化執行（可選）
用 cron 定時執行（每 5 分鐘同步一次）：
```bash
# 編輯 crontab
crontab -e

# 加入這一行
*/5 * * * * /Users/nomisas/sync-photos-r2.sh
```

---

## ✅ 驗證清單

完成所有步驟後，檢查：

- [ ] R2 Bucket 已建立 (`nomi-event-live-gallery`)
- [ ] API Token 已生成並保存
- [ ] rclone 已安裝 (`rclone version` 有輸出)
- [ ] rclone config 已設置 (`rclone config show`)
- [ ] 測試照片已上傳到 R2
- [ ] 測試 URL 可訪問 (在瀏覽器中看到照片)
- [ ] 全部照片已同步到 R2
- [ ] manifest.json 已更新新 URL
- [ ] index.html 的 IMAGE_BASE_URL 已修改
- [ ] GitHub 上已推送更新

---

## 🎯 下一步

1. 按上述步驟完成設定
2. 推送更新到 GitHub
3. Cloudflare Pages 會自動重新部署
4. 訪問你的網址應該能看到照片正確加載

---

## 📍 常用 rclone 命令

```bash
# 列出 bucket 內容
rclone ls r2-live-gallery:

# 列出特定路徑
rclone ls r2-live-gallery:photos/

# 刪除檔案
rclone delete r2-live-gallery:photos/oldfile.jpg

# 檢查差異（不同步）
rclone check /local/path r2-live-gallery:remote-path/

# 同步並刪除遠端多餘的檔案
rclone sync --delete-excluded /local/path r2-live-gallery:remote-path/
```

---

**準備開始？告訴我你完成到哪一步！** 🚀
