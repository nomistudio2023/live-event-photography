# Live Event Photography Project - 部署規劃報告 (2026-01-21)

## 📅 會議摘要
**討論主題**: 活動網站上線部署方案選定
**討論日期**: 2026-01-21
**最終決定**: Cloudflare Pages 免費域名方案

---

## 🎯 核心需求分析

### 原始詢問
1. **Cloudflare R2 用途確認**: 能否同時託管靜態網頁 + 照片？
   - ✅ **答案**: 可以，R2 支援存放任何靜態資源

2. **隱藏服務商身份**: 活動網址是否能脫離品牌網站識別？
   - ✅ **答案**: 可以，透過自訂域名或獨立服務商

3. **子域名方案**: 現有 A2Hosting 主機是否能用子域名部署？
   - ✅ **答案**: 可以，多種方式實現

---

## 📊 評估的三種部署方案

### 方案 A：子域名 → Cloudflare Pages（最終選定 ✅）
```
架構：
GitHub repository → Cloudflare Pages → your-project.pages.dev

優點：
✅ 免費 + 自動 HTTPS
✅ 全球 CDN 加速
✅ 自動部署（push GitHub → 直接上線）
✅ 無需設定 A2Hosting DNS
✅ 簡單快速

缺點：
❌ 域名顯示為 Cloudflare Pages（暫時可接受）
❌ 需要透過 GitHub 管理檔案

使用時機：
✓ 暫時無自訂域名需求
✓ 快速上線優先
✓ 初期測試部署
```

### 方案 B：子域名 → A2Hosting 另一個 WordPress 實例
```
架構：
event.lara-studio.com → A2Hosting cPanel 子域名設定

優點：
✅ 在現有主機上，無需額外學習
✅ 完整 WordPress 功能
✅ 域名隱蔽（event.lara-studio.com）

缺點：
❌ 佔用主機資源
❌ 相比 Cloudflare Pages 速度較慢
❌ 無法自動同步照片（需手動管理）
❌ 不是專門 CDN，海外用戶延遲高

使用時機：
✗ 不推薦此方案
```

### 方案 C：子域名 → Cloudflare R2 + Workers（進階）
```
架構：
event.lara-studio.com → Cloudflare Workers → R2 Bucket

優點：
✅ 完全隱蔽 + 專業感
✅ 超快速（真正 CDN）
✅ 可實現複雜邏輯

缺點：
❌ 需要程式設定知識
❌ 學習曲線較陡

使用時機：
✓ 未來自訂域名就緒後升級方案
```

---

## 🏆 最終決定：Cloudflare Pages 免費域名

### 決定理由
1. **快速上線**: 最少配置，最快部署
2. **成本效益**: 完全免費，無額外費用
3. **無需 A2Hosting 參與**: DNS 管理無關
4. **暫時方案**: 未來可升級至自訂域名

### 清晰的流程圖
```
本地處理
└─ photos_web/
   (index.html + CSS/JS + 照片)
        ↓
   GitHub repository
        ↓
   Cloudflare Pages
   (自動部署)
        ↓
   活動網址：
   https://[your-project].pages.dev/
```

### DNS 角色澄清
| 元件 | 角色 | 需要 A2Hosting 嗎？ |
|------|------|-------------------|
| **GitHub** | 存放程式碼 | ❌ 不需要 |
| **Cloudflare Pages** | 部署 + 執行網站 | ❌ 不需要 |
| **A2Hosting** | 主網站託管 (WordPress) | ✅ 需要（但與活動網站無關） |

---

## 🚀 下一步行動計畫

### Phase 1：GitHub 準備
- [ ] 建立 GitHub 帳號（若無）
- [ ] 建立新 repository: `live-event-photography`
- [ ] 上傳 `photos_web/` 內容到 repository
  - [ ] index.html
  - [ ] 所有 CSS/JS 檔案
  - [ ] manifest.json
  - [ ] photos/ 資料夾

### Phase 2：Cloudflare Pages 部署
- [ ] 註冊 Cloudflare 帳號（免費）
- [ ] 在 Cloudflare Pages 連接 GitHub repository
- [ ] 設定自動部署
- [ ] 取得活動網址: `https://[project-name].pages.dev/`

### Phase 3：自動化同步（後期優化）
- [ ] 設定 GitHub Actions 或 rclone
- [ ] 本地照片變化 → 自動推送到 GitHub
- [ ] Cloudflare Pages 自動更新

### Phase 4：升級方案（未來）
- [ ] 購買自訂域名（如 event.lara-studio.com）
- [ ] 升級為方案 C（R2 + Workers）
- [ ] 完全隱蔽品牌身份

---

## 📝 技術規格回顧

### 現有系統
```
後端處理：
✅ auto_compress_v2.py    (影像處理引擎)
✅ config.json            (集中設定)
✅ photos_web/            (成品資料夾)

前端展示：
✅ index.html             (V3.1 瀑布流 + 燈箱)
✅ manifest.json          (照片清單)
```

### 部署前檢查清單
- [ ] manifest.json 內照片路徑是否正確
- [ ] index.html 內 CSS/JS 路徑是否相對路徑
- [ ] 照片是否已壓縮優化（by auto_compress_v2.py）
- [ ] 浮水印設定是否符合需求

---

## 💡 重點總結

| 項目 | 決定 |
|------|------|
| **部署平台** | Cloudflare Pages |
| **域名策略** | 免費域名（暫時） |
| **DNS 管理** | 無需 A2Hosting 參與 |
| **自動化** | GitHub push → 自動上線 |
| **隱蔽性** | 暫時看得出是 Cloudflare Pages |
| **升級路徑** | 未來可升級至自訂域名 + R2 |

---

## 📚 參考資源

### 相關文件
- `project_status_20260118.md` - 原始功能規格 (Spec v3.1)
- `auto_compress_v2.py` - 影像處理引擎
- `config.json` - 系統設定

### 下一次討論焦點
1. GitHub repository 建立詳細步驟
2. 自動化同步方案設計
3. 升級至自訂域名的時間表

---

**狀態**: ✅ 部署方案已確定，等待執行
**更新日期**: 2026-01-21
**負責人**: nomisas
