# Implementation Plan: Watermark Advanced Options

**Branch**: `002-watermark-advanced` | **Date**: 2026-02-11 | **Spec**: [spec.md](./spec.md)

## Summary

為浮水印系統增加三項進階功能：字型選擇、即時預覽（Canvas-based）、拖拽定位。涉及後端（新增 API + 修改 `_apply_watermark`）和前端（Admin Settings 面板改造）。

## Technical Context

**Language/Version**: Python 3.10+ (backend), Vanilla JS ES2020+ (frontend)  
**Primary Dependencies**: Pillow (PIL), Tailwind CSS (CDN)  
**Storage**: `config/config.json` (watermark settings)  
**Testing**: 手動測試（發布照片驗證）  
**Target Platform**: Desktop Chrome/Safari（Admin 主要在桌面使用）  
**Constraints**: 不引入新 Python 依賴、不引入前端框架

## Constitution Check

| Principle | Status | Note |
|-----------|--------|------|
| I. Config-Driven | ✅ Plan | 字型名稱和自訂座標存入 config.json |
| II. Consistent API | ✅ Plan | 新 API `GET /api/available-fonts` 遵循統一格式 |
| III. Python Style | ✅ Plan | 新程式碼遵循 snake_case + logger |
| IV. Frontend Conventions | ✅ Plan | 新 JS 用 addEventListener + camelCase |
| V. Documentation | ✅ Plan | 更新 changelog + project-status |
| VI. Single Source of Truth | ✅ Plan | 字型設定統一存在 config.json |
| VII. Graceful Degradation | ✅ Plan | 字型不可用時回退到系統預設 |

## Architecture Design

### 新增 API

```
GET /api/available-fonts
Response: {
    "status": "success",
    "data": [
        {"name": "PingFang SC", "path": "/System/Library/Fonts/PingFang.ttc", "supports_cjk": true},
        {"name": "Helvetica", "path": "/System/Library/Fonts/Helvetica.ttc", "supports_cjk": false},
        ...
    ]
}
```

### Config 擴充

在 `config/config.json` 的 `processing.watermark` 中新增：

```json
{
    "processing": {
        "watermark": {
            "text_font_name": "PingFang SC",
            "position": "custom",
            "custom_x_percent": 85.0,
            "custom_y_percent": 90.0
        }
    }
}
```

當 `position` 為 `"custom"` 時，使用 `custom_x_percent` 和 `custom_y_percent`（百分比座標）。

### 前端預覽架構

```
Admin Settings Panel
├── Watermark Settings Section (existing)
│   ├── Type Toggle: Text / Image
│   ├── Text Content Input
│   ├── Font Selector (NEW) ← dropdown from /api/available-fonts
│   ├── Font Size Slider
│   ├── Position Selector (existing 7 presets + "Custom")
│   ├── Opacity Slider
│   └── Size/Margin Sliders
│
├── Preview Canvas (NEW)
│   ├── Background: Buffer 第一張照片（縮小到 Canvas 尺寸）
│   ├── Overlay: Canvas 2D 渲染的浮水印
│   └── Drag Handler: mousedown/mousemove/mouseup on watermark area
│
└── Save Button
```

Canvas 渲染流程：
```javascript
function renderWatermarkPreview() {
    const ctx = previewCanvas.getContext('2d');
    // 1. 繪製背景照片
    ctx.drawImage(backgroundImg, 0, 0, canvasWidth, canvasHeight);
    // 2. 根據設定繪製浮水印
    if (watermarkType === 'text') {
        ctx.font = `${fontSize}px "${fontName}"`;
        ctx.fillStyle = `rgba(${r},${g},${b},${opacity})`;
        ctx.fillText(text, x, y);
    } else {
        ctx.globalAlpha = opacity;
        ctx.drawImage(watermarkImg, x, y, wmWidth, wmHeight);
    }
}
```

## Implementation Phases

### Phase 1: 後端字型 API + 字型名稱支援（~0.5 天）

**server.py 修改**:

1. 新增 `GET /api/available-fonts` 端點：
   - 掃描已知系統字型路徑
   - 嘗試用 PIL 載入驗證可用性
   - 標記 CJK 支援（嘗試渲染「測試」兩字）
   - 回傳可用字型列表

2. 修改 `_apply_watermark()` 的字型載入邏輯：
   - 讀取 `config.processing.watermark.text_font_name`
   - 從字型列表中找到對應路徑
   - 找不到時回退到 PingFang → default

3. 修改 `_calculate_watermark_position()`：
   - 新增 `position == "custom"` 分支
   - 讀取 `custom_x_percent` / `custom_y_percent`
   - 轉換百分比為像素座標

### Phase 2: 前端字型選擇器（~0.5 天）

**admin.html 修改**:

1. 在 Watermark Settings 區域新增字型下拉選單
2. 頁面載入時呼叫 `/api/available-fonts` 填充選項
3. CJK 字型標記 `(中文)` 標籤方便識別
4. 選擇變更時更新 config 並觸發預覽重繪

### Phase 3: Canvas 即時預覽（~1 天）

**admin.html 修改**:

1. 在 Watermark Settings 下方新增 `<canvas>` 預覽區域（400×267px，3:2 比例）
2. 實作 `WatermarkPreview` 物件：
   - `loadBackground()`: 從 `/api/buffer` 取第一張照片作為背景
   - `render()`: 根據當前設定在 Canvas 上繪製浮水印
   - 所有設定控制項的 `input` / `change` 事件觸發 `render()`
3. 字型預載入：用 `FontFace` API 載入選定字型到瀏覽器

### Phase 4: 拖拽定位（~0.5 天）

**admin.html 修改**:

1. 在 Canvas 上實作拖拽邏輯：
   ```javascript
   canvas.addEventListener('mousedown', startDrag);
   canvas.addEventListener('mousemove', onDrag);
   canvas.addEventListener('mouseup', endDrag);
   ```
2. 拖拽開始時檢測滑鼠是否在浮水印區域內
3. 拖拽中即時更新浮水印位置並重繪
4. 拖拽結束時計算百分比座標，更新位置下拉為「Custom」
5. 選擇預設位置時清除自訂座標

## File Changes

| 檔案 | 變更類型 | 說明 |
|------|----------|------|
| `server.py` | 修改 | 新增 `/api/available-fonts`、修改 `_apply_watermark()` + `_calculate_watermark_position()` |
| `templates/admin.html` | 修改 | 字型選擇器 + Canvas 預覽 + 拖拽邏輯 |
| `config/config.json` | 修改 | 新增 `text_font_name`、`custom_x_percent`、`custom_y_percent` |
| `docs/dev/changelog.md` | 修改 | 新增 changelog 條目 |

## Risk Assessment

| 風險 | 可能性 | 影響 | 緩解 |
|------|--------|------|------|
| Canvas 渲染的字型與 PIL 渲染不一致 | 高 | 中 | 預覽加上「實際效果可能略有差異」提示；使用相同字型檔案 |
| 系統字型路徑在不同 macOS 版本不同 | 中 | 中 | 掃描多個已知路徑 + PIL 驗證可用性 |
| 自訂座標在不同比例照片上偏移 | 中 | 低 | 使用百分比座標而非絕對像素 |
| Canvas 字型載入時機問題（字型未載入完就渲染） | 中 | 低 | 使用 `FontFace.load()` Promise 確保載入完成 |

## Estimated Timeline

| Phase | 工作量 | 累計 |
|-------|--------|------|
| Phase 1: 後端字型 API + 支援 | 0.5 天 | 0.5 天 |
| Phase 2: 前端字型選擇器 | 0.5 天 | 1.0 天 |
| Phase 3: Canvas 即時預覽 | 1.0 天 | 2.0 天 |
| Phase 4: 拖拽定位 | 0.5 天 | 2.5 天 |
| **Total** | **2.5 天** | |
