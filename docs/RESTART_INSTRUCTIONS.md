# 重啟服務器說明 - 應用隱藏文件修復

## ✅ 已完成的修改

### 1. 禁用 macOS 資源分叉 ✅
- ✅ `server.py` - 已添加 `COPYFILE_DISABLE=1`
- ✅ `sync_to_r2.py` - 已添加 `COPYFILE_DISABLE=1`

### 2. 加強清理機制 ✅
- ✅ `update_manifest()` - 發布前清理、更新後驗證
- ✅ 發布流程 - 雙重驗證機制

---

## 🔄 重啟步驟

### 1. 停止當前服務器

**Terminal 1 (server.py)**：
- 按 `Ctrl+C` 停止

**Terminal 2 (sync_to_r2.py)**：
- 按 `Ctrl+C` 停止

### 2. 重新啟動服務器

**Terminal 1**：
```bash
cd /Users/nomisas/.gemini/antigravity/scratch/live-event-photography
python3 server.py
```

**Terminal 2**：
```bash
cd /Users/nomisas/.gemini/antigravity/scratch/live-event-photography
python3 sync_to_r2.py
```

### 3. 或使用 Mac App

如果使用 Mac App：
1. 關閉當前運行的 App
2. 重新啟動 App

---

## ✅ 驗證修復

### 測試步驟

1. **發布一張新照片**
2. **檢查是否產生隱藏文件**：
   ```bash
   ls -la /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web | grep "\._"
   ```
3. **如果沒有 `._` 文件**：✅ 成功
4. **檢查 manifest.json**：
   ```bash
   cat /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web/manifest.json
   ```
5. **確認無隱藏文件條目**：✅ 成功

---

## 📋 修改摘要

### server.py
- 添加 `os.environ['COPYFILE_DISABLE'] = '1'`（第 17-18 行）
- 加強 `update_manifest()` 函數（發布前清理、最終驗證）
- 加強發布流程（雙重驗證）

### sync_to_r2.py
- 添加 `os.environ['COPYFILE_DISABLE'] = '1'`
- 更新 `get_r2_photos()` 過濾隱藏文件
- 更新 `update_r2_manifest()` 過濾隱藏文件

---

## ⚠️ 重要提醒

1. **必須重啟服務器**：環境變數只在程序啟動時生效
2. **只影響 Python 代碼**：Finder 複製文件仍可能產生隱藏文件
3. **已存在的隱藏文件**：需要手動清理（使用 `cleanup_hidden_files.py`）

---

## 🛠️ 如果仍有問題

### 清理現有隱藏文件
```bash
python3 cleanup_hidden_files.py
```

### 使用系統工具清理
```bash
./cleanup_dot_files.sh
```

### 修復 R2 manifest
```bash
python3 fix_r2_manifest.py
```

---

**狀態**: ✅ **已修改，請重啟服務器**
