# Implementation Plan: Mobile Admin UI

**Branch**: `001-mobile-admin-ui` | **Date**: 2026-02-11 | **Spec**: [spec.md](./spec.md)

## Summary

為現有的 `templates/admin.html` 增加 responsive 支援，使其在手機（≤480px）上以單欄+底部導覽呈現，平板（≥768px）上以雙欄呈現，桌面（≥1024px）維持現有三欄佈局。所有變更限制在 `admin.html` 單一檔案內，不需要修改後端。

## Technical Context

**Language/Version**: HTML5 + Vanilla JavaScript (ES2020+)  
**Primary Dependencies**: Tailwind CSS v3 (CDN)  
**Storage**: N/A（純前端改動）  
**Testing**: 手動測試 + Chrome DevTools 模擬  
**Target Platform**: Mobile Safari (iOS 15+), Chrome Mobile, Desktop Chrome/Safari  
**Project Type**: Single-file enhancement (admin.html)  
**Constraints**: 零後端修改、零新依賴、不破壞桌面端現有功能

## Constitution Check

| Principle | Status | Note |
|-----------|--------|------|
| I. Config-Driven | ✅ Pass | Breakpoint 值用 CSS 變數，不硬編碼 |
| II. Consistent API | ✅ N/A | 不修改 API |
| III. Python Style | ✅ N/A | 不修改 Python |
| IV. Frontend Conventions | ⚠️ Enforce | 新 JS 程式碼 MUST 用 `addEventListener`，不用 inline onclick |
| V. Documentation | ✅ Plan | 完成後更新 changelog |
| VI. Single Source of Truth | ✅ Pass | |
| VII. Graceful Degradation | ✅ Plan | 網路失敗有重試提示 |

## Architecture Design

### Responsive 策略：CSS Media Queries + JS Layout Manager

不使用「建立獨立 mobile 頁面」的方案，而是在同一個 `admin.html` 中用 CSS Media Queries 控制佈局，搭配少量 JS 處理 Mobile 專屬的 UI 行為。

```
Breakpoints:
  ≤480px   → Mobile:  單欄 + 底部導覽 + 全螢幕預覽
  481-767px → Phone-L: 同 Mobile（底部導覽）
  ≥768px   → Tablet:  雙欄（Inbox + Preview）
  ≥1024px  → Desktop: 三欄（維持現狀）
```

### 佈局結構改動

```
現有結構:
<main class="flex-1 flex overflow-hidden">       ← 水平 flex 三欄
  <section id="col-inbox" style="width:320px">   ← 固定寬度
  <section id="col-preview" class="flex-1">      ← 彈性寬度
  <section id="col-livefeed" style="width:280px"> ← 固定寬度
</main>

改造後:
<main id="main-container" class="flex-1 flex overflow-hidden">
  <!-- 桌面：三欄並排 / 平板：兩欄並排 / 手機：只顯示當前分頁 -->
  <section id="col-inbox">      ← 手機分頁 1
  <section id="col-preview">    ← 手機全螢幕覆蓋
  <section id="col-livefeed">   ← 手機分頁 2
</main>

<!-- Mobile Only: 底部導覽 -->
<nav id="mobile-nav" class="fixed bottom-0 ... lg:hidden">
  <button data-tab="inbox">📥 Inbox</button>
  <button data-tab="published">📤 Published</button>
  <button data-tab="settings">⚙️ Settings</button>
</nav>
```

### Mobile 照片預覽：Full-Screen Overlay

```html
<!-- 手機預覽覆蓋層 -->
<div id="mobile-preview-overlay" class="fixed inset-0 z-50 bg-black hidden md:hidden">
  <img id="mobile-preview-img" class="w-full h-[60vh] object-contain">
  <div class="p-4">
    <label>曝光</label>
    <input type="range" min="-2" max="2" step="0.1" id="mobile-exposure">
    <div class="flex gap-3 mt-4">
      <button id="mobile-btn-skip" class="flex-1 h-12 ...">⏭ 跳過</button>
      <button id="mobile-btn-rotate" class="h-12 w-12 ...">🔄</button>
      <button id="mobile-btn-publish" class="flex-1 h-12 ...">🚀 發布</button>
    </div>
  </div>
</div>
```

### 觸控手勢

使用原生 `touchstart` / `touchend` 事件（index.html 已有此模式），不引入外部手勢庫：

```javascript
// 左右滑動切換照片
let touchStartX = 0;
mobilePreviewOverlay.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
});
mobilePreviewOverlay.addEventListener('touchend', (e) => {
    const diff = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(diff) > 50) {
        diff > 0 ? prevPhoto() : nextPhoto();
    }
});
```

## Implementation Phases

### Phase 1: CSS Responsive 基礎（~0.5 天）

修改 `admin.html` 的 CSS：

1. 將三個 column 的固定寬度改為 responsive：
   - Desktop（≥1024px）: 維持現有 `320px / flex-1 / 280px`
   - Tablet（≥768px）: `280px / flex-1`，隱藏 col-livefeed
   - Mobile（<768px）: 每個 column 佔滿寬度，一次只顯示一個

2. 新增 CSS Media Queries：
   ```css
   @media (max-width: 1023px) {
       #col-livefeed { display: none; }
       #col-inbox { width: 280px; }
   }
   @media (max-width: 767px) {
       #main-container { flex-direction: column; }
       #col-inbox, #col-preview { width: 100%; }
       .desktop-only { display: none; }
       .mobile-only { display: block; }
       body { padding-bottom: 56px; } /* 底部導覽空間 */
   }
   ```

3. 新增 Mobile 底部導覽列 HTML + CSS

### Phase 2: Mobile 分頁切換邏輯（~0.5 天）

新增 `LayoutManager` JS 模組：

```javascript
const LayoutManager = {
    currentTab: 'inbox',
    isMobile: () => window.innerWidth < 768,

    switchTab(tab) {
        if (!this.isMobile()) return;
        this.currentTab = tab;
        document.getElementById('col-inbox').classList.toggle('hidden', tab !== 'inbox');
        document.getElementById('col-preview').classList.toggle('hidden', tab !== 'inbox');
        // published 用 col-inbox 的下半部
        this.updateNavHighlight(tab);
    },

    init() {
        window.addEventListener('resize', () => this.handleResize());
        this.handleResize();
    },

    handleResize() {
        const mobile = this.isMobile();
        document.getElementById('mobile-nav')?.classList.toggle('hidden', !mobile);
        if (!mobile) {
            // 桌面模式：顯示所有欄位
            ['col-inbox', 'col-preview', 'col-livefeed'].forEach(id => {
                document.getElementById(id)?.classList.remove('hidden');
            });
        }
    }
};
```

### Phase 3: Mobile 全螢幕預覽 + 編輯（~1 天）

1. 建立 `mobile-preview-overlay` HTML 結構
2. 實作觸控手勢（左右滑動切換）
3. 實作簡化編輯控制（曝光滑桿 + 旋轉按鈕）
4. 連接現有 `publishImage()` API（加上防抖）
5. 發布成功後自動跳到下一張

### Phase 4: 觸控優化 + 測試（~0.5 天）

1. 所有按鈕最小 44×44px 觸控區域
2. 防止 iOS Safari 的 bounce scrolling
3. 在 Chrome DevTools 模擬以下裝置測試：
   - iPhone 14 (390×844)
   - iPhone SE (375×667)
   - iPad (768×1024)
   - iPad Pro (1024×1366)
4. 驗證桌面端無回歸

## File Changes

| 檔案 | 變更類型 | 說明 |
|------|----------|------|
| `templates/admin.html` | 修改 | 主要改動：CSS Media Queries + Mobile Nav + Preview Overlay + LayoutManager JS |
| `docs/dev/changelog.md` | 修改 | 新增 changelog 條目 |
| `docs/reference/project-status.md` | 修改 | 更新 Mobile Admin UI 狀態為已完成 |

**不修改**: `server.py`、`sync_to_r2.py`、`index.html`、任何 config 檔案

## Risk Assessment

| 風險 | 可能性 | 影響 | 緩解 |
|------|--------|------|------|
| 桌面端佈局被 Media Queries 影響 | 中 | 高 | 所有 mobile CSS 限制在 `@media (max-width: ...)` 內 |
| Tailwind CDN 的 responsive utilities 與自訂 CSS 衝突 | 低 | 中 | 優先使用 Tailwind 的 `md:` `lg:` 前綴 |
| iOS Safari 的 viewport 高度計算問題（100vh 包含地址欄） | 高 | 中 | 使用 `dvh` 單位或 JS 動態計算 |
| 現有 keyboard shortcuts 在 mobile 上干擾輸入 | 中 | 低 | Mobile 模式下禁用 keyboard shortcuts |

## Estimated Timeline

| Phase | 工作量 | 累計 |
|-------|--------|------|
| Phase 1: CSS Responsive | 0.5 天 | 0.5 天 |
| Phase 2: 分頁切換 | 0.5 天 | 1.0 天 |
| Phase 3: 全螢幕預覽 | 1.0 天 | 2.0 天 |
| Phase 4: 觸控優化+測試 | 0.5 天 | 2.5 天 |
| **Total** | **2.5 天** | |
