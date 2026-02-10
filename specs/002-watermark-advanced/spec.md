# Feature Specification: Watermark Advanced Options

**Feature Branch**: `002-watermark-advanced`  
**Created**: 2026-02-11  
**Status**: Draft  
**Constitution**: v1.0.0

## Background

目前浮水印系統已支援基礎功能：文字/圖片浮水印、7 個預設位置、透明度調整、大小縮放、邊距控制。但有三個缺口：

1. **字型選擇**：文字浮水印的字型是在伺服器端硬編碼 fallback（PingFang → STHeiti → Helvetica → default），使用者無法在 Admin UI 選擇字型
2. **視覺化定位**：位置只能從 7 個預設值選擇（`bottom-right` 等），無法精確控制座標
3. **即時預覽**：Admin UI 的浮水印設定面板修改後，需要實際發布一張照片才能看到效果

## User Scenarios & Testing

### User Story 1 — 選擇浮水印字型 (Priority: P1)

活動攝影師想要為不同客戶的活動使用不同風格的文字浮水印——有的需要優雅的手寫體，有的需要正式的黑體。

**Why this priority**: 字型是文字浮水印視覺效果最關鍵的因素，目前完全無法控制。

**Independent Test**: 在 Admin Settings 中選擇不同字型，發布一張照片驗證字型變更。

**Acceptance Scenarios**:

1. **Given** Admin Settings 的 Watermark 面板中，**When** 浮水印類型為「文字」，**Then** 顯示字型選擇下拉選單，列出可用字型
2. **Given** 字型下拉選單展開，**When** 選擇一個字型，**Then** 預覽區域即時更新顯示該字型效果
3. **Given** 選擇了新字型並儲存，**When** 發布一張照片，**Then** 照片上的浮水印使用選定的字型

---

### User Story 2 — 浮水印即時預覽 (Priority: P1)

使用者調整浮水印設定（文字內容、字型、大小、位置、透明度）時，想要即時看到效果，而不需要每次都發布一張照片。

**Why this priority**: 沒有預覽功能，每次調整都要「改設定 → 發布照片 → 檢查效果」，體驗極差。

**Independent Test**: 修改浮水印文字和大小，預覽區即時顯示更新的效果。

**Acceptance Scenarios**:

1. **Given** Watermark 設定面板開啟，**When** 修改任一參數（文字/字型/大小/位置/透明度），**Then** 預覽區域在 200ms 內更新
2. **Given** 預覽區域顯示中，**When** 預覽使用一張已有的 Buffer 照片作為背景，**Then** 浮水印疊加在照片上顯示真實效果
3. **Given** 預覽效果滿意並點擊儲存，**When** 後續發布照片，**Then** 照片上的浮水印與預覽一致

---

### User Story 3 — 拖拽定位浮水印 (Priority: P2)

使用者想要將浮水印精確放置在照片的特定位置，而不僅限於 7 個預設位置。

**Why this priority**: 大部分場景下預設位置夠用，但偶爾需要微調（如避開照片主體）。

**Independent Test**: 在預覽區域中拖拽浮水印到自訂位置，儲存後發布照片驗證位置。

**Acceptance Scenarios**:

1. **Given** 預覽區域中有浮水印顯示，**When** 滑鼠按住浮水印拖拽，**Then** 浮水印跟隨滑鼠移動
2. **Given** 拖拽完成放開滑鼠，**When** 查看位置設定，**Then** 下拉選單顯示「自訂」，座標值已更新
3. **Given** 選擇預設位置（如 bottom-right），**When** 點擊該選項，**Then** 浮水印回到預設位置，覆蓋自訂座標

---

### Edge Cases

- 選擇的字型不支援中文字元時，MUST 回退到 PingFang 或系統預設中文字型
- 浮水印拖拽到照片邊界外時，MUST 限制在照片範圍內
- 浮水印圖片損壞或遺失時，預覽 MUST 顯示提示訊息而非白框
- 文字浮水印長度極長（>50 字元）時，預覽 MUST 自動縮小或截斷

## Requirements

### Functional Requirements

- **FR-001**: Admin Watermark 設定面板 MUST 增加字型選擇下拉選單
- **FR-002**: 字型列表 MUST 透過後端 API 取得（讀取系統可用字型），不得在前端硬編碼
- **FR-003**: 設定面板 MUST 包含浮水印即時預覽區域（≥300px 寬）
- **FR-004**: 預覽 MUST 使用前端 Canvas 渲染，不需呼叫後端 API
- **FR-005**: 預覽背景 MUST 使用 Buffer 中的第一張照片（若 Buffer 為空，用預設灰底）
- **FR-006**: 拖拽定位功能 MUST 記錄座標比例（百分比），使其適用於不同尺寸的照片
- **FR-007**: 浮水印設定（含字型名稱和自訂座標）MUST 儲存到 `config/config.json`
- **FR-008**: 後端 `_apply_watermark()` MUST 支援讀取自訂座標和指定字型名稱
- **FR-009**: 新增 API `GET /api/available-fonts` 回傳伺服器可用字型列表

### Key Entities

- **Font**: `{name, path, supports_cjk}` — 伺服器可用字型
- **WatermarkPosition**: `{preset: string | null, custom_x_percent: float, custom_y_percent: float}` — 位置（預設或自訂百分比）
- **WatermarkPreview**: 前端 Canvas 渲染，不涉及後端

## Success Criteria

### Measurable Outcomes

- **SC-001**: 使用者可在 Admin 中從至少 5 個字型中選擇一個，發布照片驗證字型正確
- **SC-002**: 修改浮水印任一參數後，預覽在 200ms 內更新（Canvas 渲染無延遲感）
- **SC-003**: 拖拽浮水印到自訂位置並儲存後，發布照片的浮水印位置偏差 ≤ 5% 照片尺寸
- **SC-004**: 所有現有浮水印功能（文字/圖片、預設位置、透明度）零回歸
