# Live Event Photography - 後續開發路線圖

**建立日期**: 2026-01-23  
**專案狀態**: 核心功能已完成，進入優化階段

---

## 📊 當前專案狀態評估

### ✅ 已完成的核心功能

1. **照片處理流程** ✓
   - 相機 → photos_buffer → Admin 選擇/編輯 → photos_web → R2 同步 → 網站顯示
   - 所有環節已打通並運作正常

2. **照片編輯功能** ✓
   - Exposure: -2.0 ~ +2.0
   - Rotation: 0°, 90°, 180°, 270°
   - Straighten: -10° ~ +10°
   - Scale: 0.5 ~ 2.0

3. **Sequential Filename 策略** ✓
   - 已實現 `get_next_publish_filename()` 函數
   - 支援同一照片多次發布（15D_7109.jpg → 15D_7109_002.jpg）

4. **Batch Publish 功能** ✓
   - `/api/batch_publish` 端點已實現
   - 支援批量發布多張照片

5. **R2 同步機制** ✓
   - `sync_to_r2.py` 自動同步腳本運作正常
   - 安全模式（只新增不刪除）
   - 自動更新 manifest.json

6. **Admin UI** ✓
   - 三欄佈局（Buffer / Preview / Live Feed）
   - 快捷鍵支援
   - 實時統計
   - 同步狀態指示器

---

## 🎯 待優化項目（按優先級排序）

### 🔴 高優先級

#### 1. **Cloudflare Functions 部署檢查**
**狀態**: 需要確認  
**描述**: 根據開發進度文件，需要 `functions/photo/[[path]].js` 來代理 R2 照片

**檢查項目**:
- [ ] 確認 functions 目錄是否存在
- [ ] 檢查 Cloudflare Pages 部署配置
- [ ] 驗證 R2 綁定（GALLERY）是否正確

**建議行動**:
```bash
# 檢查是否有 functions 目錄
ls -la functions/photo/ 2>/dev/null || echo "需要創建 functions 目錄"
```

---

#### 2. **Batch Publish 功能增強**
**狀態**: 部分完成  
**當前實現**: 僅支援批量發布，但所有照片使用相同曝光參數

**需要改進**:
- [ ] 支援每張照片獨立設定編輯參數（exposure, rotation, straighten, scale）
- [ ] Admin UI 增加批量選擇和編輯介面
- [ ] 預覽批量編輯效果

**建議實現**:
```python
# 新的 API 設計
class BatchPublishRequest(BaseModel):
    items: List[Dict[str, Any]]  # 每張照片的獨立參數
    # [{"filename": "IMG_1.jpg", "exposure": 0.5, "rotation": 90}, ...]
```

---

#### 3. **EXIF Metadata 保留**
**狀態**: 未實現  
**問題**: Pillow 處理照片時會丟失 EXIF 資訊（拍攝時間、相機型號等）

**影響**: 
- 無法保留照片的原始拍攝資訊
- 可能影響照片排序和組織

**建議實現**:
```python
from PIL.ExifTags import TAGS
from PIL import Image

def preserve_exif(source_path, dest_path):
    """保留 EXIF 資訊到處理後的照片"""
    # 1. 讀取原始 EXIF
    # 2. 處理照片
    # 3. 將 EXIF 寫回處理後的照片
```

**參考資源**:
- `Pillow` 的 `Image.getexif()` 和 `Image.save(exif=...)`
- 或使用 `piexif` 庫進行更精細的 EXIF 操作

---

### 🟡 中優先級

#### 4. **Mobile Admin UI 適配**
**狀態**: 未實現  
**描述**: 當前 Admin UI 主要針對桌面端設計，手機操作不便

**需要改進**:
- [ ] 響應式佈局優化（三欄改為單欄/雙欄）
- [ ] 觸控手勢支援（滑動切換照片）
- [ ] 簡化編輯控制項（適合小螢幕）
- [ ] 快捷鍵改為觸控按鈕

**建議實現**:
- 使用 CSS Media Queries 檢測螢幕尺寸
- 在手機端隱藏部分功能，保留核心操作
- 考慮使用 PWA 技術，支援離線操作

---

#### 5. **R2 Manifest 緩存優化**
**狀態**: 部分解決（使用時間戳）  
**當前方案**: 前端加時間戳繞過緩存

**可以改進**:
- [ ] 使用版本號而非時間戳（更可控）
- [ ] 考慮使用 Cloudflare Edge Cache API
- [ ] 實現 manifest 版本管理

**建議實現**:
```python
# manifest.json 結構改進
{
  "version": "20260123-143022",  # 版本號
  "updated_at": "2026-01-23T14:30:22Z",
  "photos": [...]
}
```

---

### 🟢 低優先級（未來考慮）

#### 6. **照片預覽優化**
- [ ] 縮圖生成（加快載入速度）
- [ ] 懶加載（Lazy Loading）
- [ ] 無限滾動

#### 7. **統計和分析**
- [ ] 發布照片數量統計
- [ ] 最受歡迎照片（點擊率）
- [ ] 活動時間軸視覺化

#### 8. **備份和恢復**
- [ ] 自動備份 photos_web 到本地
- [ ] R2 照片版本控制
- [ ] 一鍵恢復功能

---

## 🛠️ 技術債務和改進建議

### 1. **代碼組織**
- [ ] 將 `ImageProcessor` 類拆分為獨立模組
- [ ] 統一配置管理（考慮使用 `.env` 文件）
- [ ] 增加單元測試覆蓋率

### 2. **錯誤處理**
- [ ] 增強錯誤日誌記錄
- [ ] 實現重試機制（R2 上傳失敗時）
- [ ] 用戶友好的錯誤提示

### 3. **性能優化**
- [ ] 照片處理並行化（多線程/異步）
- [ ] R2 同步批次處理（減少 API 調用）
- [ ] 前端圖片預載入策略

### 4. **安全性**
- [ ] Admin UI 增加身份驗證
- [ ] API 端點增加速率限制
- [ ] 檔案上傳驗證（防止惡意檔案）

---

## 📝 立即行動項目

### 第一步：檢查 Cloudflare Functions
```bash
# 檢查 functions 目錄
if [ ! -d "functions/photo" ]; then
    echo "需要創建 Cloudflare Functions"
    mkdir -p functions/photo
    # 創建 [[path]].js
fi
```

### 第二步：增強 Batch Publish
- 修改 `BatchPublishRequest` 模型
- 更新 `/api/batch_publish` 端點
- 更新 Admin UI 批量選擇功能

### 第三步：實現 EXIF 保留
- 研究 Pillow EXIF 處理
- 實現 `preserve_exif()` 函數
- 整合到 `ImageProcessor.process_image()`

---

## 🔍 需要確認的問題

1. **Cloudflare Functions 位置**
   - Functions 是否在另一個 Git 倉庫？
   - 是否需要在本專案中創建？

2. **R2 路徑配置**
   - `R2_PATH_PREFIX = "2026-01-20"` 是硬編碼的
   - 是否需要改為動態配置（根據活動日期）？

3. **照片命名策略**
   - 當前 Sequential Filename 是否滿足需求？
   - 是否需要更複雜的命名規則（例如：時間戳前綴）？

---

## 📚 參考資源

- [Pillow EXIF 文檔](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.getexif)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/platform/functions/)
- [FastAPI 最佳實踐](https://fastapi.tiangolo.com/tutorial/)

---

## 📅 建議開發時程

**第一週**:
- 檢查並創建 Cloudflare Functions
- 增強 Batch Publish 功能

**第二週**:
- 實現 EXIF Metadata 保留
- 開始 Mobile Admin UI 適配

**第三週**:
- 完成 Mobile Admin UI
- 優化 R2 Manifest 緩存策略

**第四週**:
- 測試和修復
- 文檔更新

---

**最後更新**: 2026-01-23  
**維護者**: 開發團隊
