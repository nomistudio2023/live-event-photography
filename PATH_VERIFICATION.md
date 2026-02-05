# 外接硬碟路徑驗證 - 2026-01-23

## 📁 當前路徑配置

### photos_web 路徑
```
/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web
```

### 完整資料夾結構
```
/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/
├── photos_buffer/    # 原始照片緩衝區
├── photos_web/       # 已發布照片（同步到 R2）
├── photos_trash/     # 已刪除照片
└── photos_archive/  # 封存照片
```

---

## ✅ 驗證結果

### 路徑配置
- ✅ **config.json 路徑正確**
- ✅ **資料夾存在且可訪問**
- ✅ **與設定一致**

### 資料夾狀態
- ✅ **有效照片**: 4 個
- ⚠️ **隱藏文件**: 需要定期清理
- ✅ **manifest.json**: 存在且無隱藏文件

---

## 📋 當前照片列表

1. `15D_7474.jpg` (467KB)
2. `15D_7475.jpg` (469KB)
3. `15D_7476.jpg` (463KB)
4. `15D_7477.jpg` (475KB)

---

## 🔧 維護建議

### 定期清理隱藏文件

**方式 1: Admin 面板**
1. 打開 Admin 面板
2. 點擊「⚙️ 設定」
3. 點擊「🧹 清理隱藏文件」

**方式 2: Terminal**
```bash
cd /Users/nomisas/.gemini/antigravity/scratch/live-event-photography
python3 cleanup_hidden_files.py
```

### 檢查路徑是否正確

如果外接硬碟路徑變更，需要：
1. 在 Admin 面板「⚙️ 設定」→「📁 資料夾設定」中更新
2. 或直接編輯 `config.json`
3. **重啟服務器**使設定生效

---

## ⚠️ 注意事項

1. **外接硬碟連接**：
   - 確保外接硬碟已連接
   - 確認路徑中的硬碟名稱正確（`詠松-2Tssd`）

2. **路徑變更**：
   - 如果硬碟名稱變更，需要更新 `config.json`
   - 更新後必須重啟服務器

3. **權限問題**：
   - 確保有讀寫權限
   - 如果出現權限錯誤，檢查資料夾權限

---

## 📊 路徑配置檢查命令

```bash
# 檢查 config.json 中的路徑
cat config.json | grep web_folder

# 檢查資料夾是否存在
ls -la "/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web"

# 檢查 manifest.json
cat "/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web/manifest.json"
```

---

**最後更新**: 2026-01-23  
**狀態**: ✅ 路徑配置正確，系統正常運作
