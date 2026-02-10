# Feature Specification: Mobile Admin UI

**Feature Branch**: `001-mobile-admin-ui`  
**Created**: 2026-02-11  
**Status**: Draft  
**Constitution**: v1.0.0

## Background

目前 Admin UI (`templates/admin.html`) 採用固定寬度三欄佈局（Column 1: 320px Inbox/Published、Column 2: flex Preview+Editor、Column 3: 可拖拽 Live Feed），整體使用 `h-screen overflow-hidden flex` 鎖定在桌面視窗。在平板或手機上完全無法操作——欄位會溢出或被壓縮到不可讀的寬度。

活動現場的攝影師助手經常需要在移動中使用手機快速審核和發布照片，目前只能回到電腦操作。

## User Scenarios & Testing

### User Story 1 — 手機上瀏覽與發布照片 (Priority: P1)

攝影師助手拿著手機，需要快速查看 Inbox 中的新照片、選擇一張、做簡單調整（曝光）後發布。

**Why this priority**: 這是活動現場最頻繁的操作，手機支援的核心價值。

**Independent Test**: 用 iPhone Safari（375px 寬）完成一次「選照片 → 調曝光 → 發布」流程。

**Acceptance Scenarios**:

1. **Given** 手機瀏覽器開啟 `localhost:8000`，**When** 頁面載入，**Then** 顯示單欄 Inbox 列表，每張照片有縮圖預覽，不需要橫向滾動
2. **Given** Inbox 列表顯示中，**When** 點擊一張照片，**Then** 進入全螢幕預覽模式，下方有曝光滑桿和發布/跳過按鈕
3. **Given** 預覽模式中，**When** 點擊「發布」按鈕，**Then** 照片以當前曝光設定發布，顯示成功 Toast，自動跳到下一張
4. **Given** 預覽模式中，**When** 點擊「跳過」或向左滑動，**Then** 跳到下一張照片，不做任何操作

---

### User Story 2 — 手機上查看已發布照片 (Priority: P2)

攝影師需要在手機上確認已發布的照片，並在需要時取消發布。

**Why this priority**: 已發布照片的管理是次要但必要的操作。

**Independent Test**: 用手機查看 Published History 列表，對一張照片執行 Unpublish。

**Acceptance Scenarios**:

1. **Given** 手機瀏覽器顯示 Admin 頁面，**When** 點擊底部導覽的「Published」分頁，**Then** 顯示已發布照片列表（含縮圖）
2. **Given** Published 列表中，**When** 長按或點擊一張照片，**Then** 顯示操作選單（取消發布/查看詳情）
3. **Given** 點擊「取消發布」，**When** 確認操作，**Then** 照片從 Published 列表移除，顯示成功 Toast

---

### User Story 3 — 平板橫式雙欄模式 (Priority: P3)

在 iPad 等平板裝置上，應該利用較大的螢幕顯示雙欄佈局。

**Why this priority**: 平板是次要使用場景，但體驗應優於手機的單欄。

**Independent Test**: 用 iPad Safari（768px 以上寬）驗證雙欄佈局。

**Acceptance Scenarios**:

1. **Given** 平板瀏覽器（≥768px）開啟 Admin 頁面，**When** 頁面載入，**Then** 左欄顯示 Inbox 列表，右欄顯示預覽+編輯器
2. **Given** 雙欄模式中，**When** 在左欄點擊照片，**Then** 右欄即時更新預覽，不需要頁面跳轉

---

### Edge Cases

- 手機旋轉（直式 ↔ 橫式）時佈局 MUST 自動適應
- 網路不穩定時，API 呼叫失敗 MUST 顯示重試提示而非白屏
- 照片尺寸極大（>10MB 的 RAW 轉 JPG）時，手機預覽 MUST 使用壓縮版
- 快速連續點擊「發布」MUST 有防抖機制，防止重複發布

## Requirements

### Functional Requirements

- **FR-001**: 系統 MUST 在 ≤480px 寬度時顯示單欄佈局（Mobile）
- **FR-002**: 系統 MUST 在 481px-767px 寬度時顯示單欄佈局加底部導覽（Large Phone/Small Tablet）
- **FR-003**: 系統 MUST 在 ≥768px 寬度時顯示雙欄佈局（Tablet）
- **FR-004**: 系統 MUST 在 ≥1024px 寬度時顯示原有三欄佈局（Desktop）
- **FR-005**: Mobile 模式 MUST 提供底部導覽列（Inbox / Published / Settings 三個分頁）
- **FR-006**: Mobile 照片預覽 MUST 為全螢幕覆蓋，含觸控手勢（左右滑動切換）
- **FR-007**: Mobile 編輯控制 MUST 簡化為：曝光滑桿 + 旋轉按鈕（隱藏 Straighten 和 Scale）
- **FR-008**: Mobile 發布操作 MUST 有大尺寸觸控按鈕（最小 44px × 44px）
- **FR-009**: 所有現有桌面功能 MUST 不受影響（純增量改動）
- **FR-010**: 統計資訊（Buffer/Live 計數）MUST 在 Mobile 模式的 Header 中顯示

### Key Entities

- **Breakpoint**: 四個響應式斷點（Mobile ≤480px、Large Phone ≤767px、Tablet ≥768px、Desktop ≥1024px）
- **Mobile Navigation**: 底部分頁導覽，取代桌面的並排欄位
- **Mobile Preview**: 全螢幕覆蓋的照片預覽+簡化編輯器

## Success Criteria

### Measurable Outcomes

- **SC-001**: 在 iPhone 14 (390px) Safari 上完成「選照 → 調曝光 → 發布」流程，全程不需橫向滾動
- **SC-002**: Mobile 單張照片的「選擇到發布」操作時間 ≤ 10 秒
- **SC-003**: 從 Desktop 到 Mobile 的佈局切換 MUST 在 100ms 內完成（無閃爍）
- **SC-004**: 桌面端所有現有功能的回歸測試通過率 100%（零破壞性變更）
- **SC-005**: 在 Chrome DevTools 的 Mobile 模擬器上，Lighthouse Performance Score ≥ 70
