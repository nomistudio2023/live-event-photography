# 手動修改活動頁面 HTML 設定教學

## 📋 概述

本文件說明如何手動修改活動頁面的 HTML 文件，包括圖片和文字的設定。

**適用場景**：
- 需要快速修改活動頁面內容
- Admin 設定功能無法滿足需求時
- 需要自訂更複雜的樣式時

---

## 📁 文件位置

活動頁面 HTML 文件位於：
```
/Users/nomisas/.gemini/antigravity/scratch/live-event-photography/index.html
```

---

## 🎨 修改活動標題和副標題

### 方法 1: 直接修改 HTML（推薦用於快速測試）

1. **打開文件**：
   ```bash
   open index.html
   # 或使用任何文字編輯器
   ```

2. **找到標題位置**（約第 449-454 行）：
   ```html
   <header class="hero" id="hero-section">
       <div class="hero-content">
           <h1 id="event-title">LIVE EVENT 2026</h1>
           <p id="event-subtitle">即時活動花絮・精彩瞬間</p>
       </div>
   </header>
   ```

3. **修改文字**：
   ```html
   <h1 id="event-title">國志電子尾牙晚宴 2026</h1>
   <p id="event-subtitle">您的活動副標題</p>
   ```

4. **保存文件**

5. **刷新瀏覽器**查看效果

### 方法 2: 修改 CSS 樣式

找到樣式定義（約第 55-66 行）：
```css
.hero-content h1 {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.6);
    letter-spacing: 2px;
    font-family: Arial, sans-serif;
}

.hero-content p {
    font-size: 1.2rem;
    color: #ddd;
    font-weight: 300;
    font-family: Arial, sans-serif;
}
```

**可修改的屬性**：
- `font-size`: 字體大小（例如：`3.5rem` 或 `56px`）
- `font-family`: 字體（例如：`"Microsoft JhengHei", Arial, sans-serif`）
- `color`: 文字顏色（例如：`#ffffff`）
- `text-shadow`: 文字陰影
- `letter-spacing`: 字距
- `font-weight`: 字體粗細（`300`, `400`, `700` 等）

---

## 🖼️ 修改背景圖片

### 方法 1: 使用線上圖片 URL

找到背景圖片設定（約第 39-49 行）：
```css
.hero {
    position: relative;
    background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.8)), 
                url('https://images.unsplash.com/photo-1492684223066-81342ee5ff30?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80') 
                no-repeat center center/cover;
    height: 50vh;
    ...
}
```

**修改方式**：
```css
background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.8)), 
            url('您的圖片URL') 
            no-repeat center center/cover;
```

### 方法 2: 使用本地圖片

1. **將圖片放到 `assets/` 資料夾**：
   ```bash
   cp /path/to/your/image.jpg assets/hero_bg.jpg
   ```

2. **修改 CSS**：
   ```css
   background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.8)), 
               url('/assets/hero_bg.jpg') 
               no-repeat center center/cover;
   ```

### 方法 3: 使用 JavaScript 動態載入（已實現）

活動頁面會自動從 `/api/event-settings` 載入設定，包括：
- `hero_image_url`: 背景圖片 URL
- `hero_image_uploaded`: 上傳的本地圖片路徑

**優先順序**：`hero_image_uploaded` > `hero_image_url`

---

## 🎯 修改其他樣式

### 修改整體顏色主題

找到 CSS 變數定義（約第 10-15 行）：
```css
:root {
    --bg-color: #121212;
    --card-bg: #1e1e1e;
    --accent-color: #3b82f6;
    --text-primary: #ffffff;
    --text-secondary: #a0a0a0;
}
```

**可修改的顏色**：
- `--bg-color`: 背景顏色
- `--card-bg`: 卡片背景顏色
- `--accent-color`: 強調色（按鈕、連結等）
- `--text-primary`: 主要文字顏色
- `--text-secondary`: 次要文字顏色

### 修改照片網格欄數

找到響應式設定（約第 17-24 行）：
```css
:root {
    --cols-desktop: 3;  /* 電腦版: 3 欄 */
    --cols-tablet: 2;   /* 平板/橫式手機 */
    --cols-mobile: 1;   /* 手機直式 */
}
```

**修改方式**：
- 增加 `--cols-desktop` 可讓電腦版顯示更多欄
- 減少可讓照片更大

---

## 📝 完整修改範例

### 範例 1: 修改標題和背景

```html
<!-- 修改標題 -->
<h1 id="event-title" style="font-size: 4rem; font-family: 'Microsoft JhengHei', sans-serif;">
    國志電子尾牙晚宴 2026
</h1>
<p id="event-subtitle" style="font-size: 1.5rem; color: #ffd700;">
    精彩瞬間・即時分享
</p>
```

```css
/* 修改背景 */
.hero {
    background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.7)), 
                url('https://your-image-url.com/image.jpg') 
                no-repeat center center/cover;
}
```

### 範例 2: 使用中文字體

```css
.hero-content h1 {
    font-family: "Microsoft JhengHei", "PingFang TC", "Heiti TC", Arial, sans-serif;
    font-size: 4rem;
    font-weight: 700;
}

.hero-content p {
    font-family: "Microsoft JhengHei", "PingFang TC", Arial, sans-serif;
    font-size: 1.3rem;
}
```

---

## ⚠️ 注意事項

1. **備份原始文件**：
   ```bash
   cp index.html index.html.backup
   ```

2. **測試修改**：
   - 修改後在瀏覽器刷新查看效果
   - 確認在不同裝置上顯示正常

3. **避免破壞 JavaScript**：
   - 不要刪除 `id` 屬性（如 `id="event-title"`）
   - 不要修改 JavaScript 相關的 class 或 id

4. **CSS 優先級**：
   - 內聯樣式（`style=""`）優先級最高
   - 如果使用 Admin 設定，JavaScript 會覆蓋 HTML 中的文字

---

## 🔄 還原修改

如果修改出錯，可以：

1. **使用備份文件**：
   ```bash
   cp index.html.backup index.html
   ```

2. **從 Git 還原**（如果有版本控制）：
   ```bash
   git checkout index.html
   ```

3. **重新下載原始文件**（如果有的話）

---

## 📚 進階修改

### 添加自訂 CSS

在 `<head>` 區塊中添加 `<style>` 標籤：

```html
<head>
    ...
    <style>
        /* 您的自訂樣式 */
        .hero-content h1 {
            /* 自訂樣式 */
        }
    </style>
</head>
```

### 修改 JavaScript 行為

找到 JavaScript 區塊（約第 496 行開始），可以修改：
- 照片載入邏輯
- 自動刷新間隔
- 燈箱行為等

---

## 🆘 常見問題

### Q: 修改後沒有生效？
A: 
1. 清除瀏覽器緩存（Cmd+Shift+R）
2. 確認文件已保存
3. 檢查語法是否正確

### Q: 如何確認修改是否正確？
A: 
1. 在瀏覽器開發者工具（F12）檢查元素
2. 查看 Console 是否有錯誤
3. 檢查 Network 標籤確認資源載入

### Q: 修改後 Admin 設定會覆蓋嗎？
A: 
- 是的，如果使用 Admin 設定，JavaScript 會每 30 秒自動更新
- 如果需要固定修改，建議直接修改 HTML 或使用 Admin 設定

---

## 📞 需要幫助？

如果遇到問題：
1. 檢查瀏覽器控制台的錯誤訊息
2. 確認 HTML/CSS 語法正確
3. 參考原始文件備份

---

**最後更新**: 2026-01-23  
**適用版本**: Live Event Photography v2.3+
