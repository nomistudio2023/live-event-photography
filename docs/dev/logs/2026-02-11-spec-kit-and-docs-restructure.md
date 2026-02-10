# 2026-02-11 開發日誌

## 📌 摘要

今日完成三項工程化改善：**文件架構重整**、**導入 Spec-Kit 開發規範**、**P2 功能規格撰寫**。目標是解決專案長期存在的「多 LLM 迭代導致風格混亂」問題，為後續開發建立可持續的結構與約束。

---

## 1. 專案狀態檢視與開發計劃

### 起因
專案 v2.3+ 核心功能已 Production Ready，但缺乏對尚未完成功能的系統性盤點。

### 執行內容
- 全面分析程式碼（`server.py`、`admin.html`、`sync_to_r2.py`）與既有文件
- 盤點出 15 個待開發項目，分為 P0（緊急修復）到 P3（未來增強）四個優先級
- 建立開發計劃文件 `docs/dev/plans/2026-02-11-development-plan.md`

### 關鍵發現
| 問題 | 嚴重度 |
|------|--------|
| `R2_PATH_PREFIX` 硬編碼在 4 個檔案 | P0 |
| Hero Banner UI 按鈕點擊無反應 | P0 |
| Batch Publish 不支援獨立編輯參數 | P1 |
| EXIF Metadata 在 PIL 處理後遺失 | P1 |
| Admin UI 無身份驗證 | P1 |
| Mobile Admin 完全無 responsive 支援 | P2 |

---

## 2. docs/ 文件架構重整

### 問題
- 18 個 `.md` 檔案全部平鋪在 `docs/` 目錄
- 三種命名風格混用：`UPPER_SNAKE.md`、`lowercase_snake.md`、`prefix_date.md`
- 3 個檔案重複講 macOS hidden files（已解決的問題）
- `README.md` 引用不存在的 `API_REFERENCE.md`、`USER_GUIDE.md`
- `R2_SETUP_GUIDE.md` 為空檔案（0 bytes）

### 執行內容
統一為 `kebab-case.md` 命名，日期檔案加 `YYYY-MM-DD-` 前綴，分類至 4 個子目錄：

```
docs/
├── README.md                    ← 索引（已更新所有連結）
├── guides/          (7 個)      ← 使用者操作指南
│   ├── getting-started.md
│   ├── operation-manual.md
│   ├── deployment.md
│   ├── r2-setup.md
│   ├── html-settings.md
│   ├── cleanup-usage.md
│   └── troubleshooting.md
├── reference/       (2 個)      ← 技術參考
│   ├── architecture.md
│   └── project-status.md
├── dev/                         ← 開發者文件
│   ├── changelog.md
│   ├── roadmap.md
│   ├── plans/                   ← 開發計劃
│   │   └── 2026-02-11-development-plan.md
│   └── logs/                    ← 開發日誌
│       ├── 2026-02-06-update.md
│       └── 2026-02-11-spec-kit-and-docs-restructure.md  ← 本文件
└── archive/         (26 個)     ← 歷史紀錄（全部統一命名）
```

- 全部使用 `git mv` 保留歷史
- 修正了 5 個檔案中的跨檔引用（`README.md`、`troubleshooting.md`、`architecture.md`、`project-status.md`、`changelog.md`）
- archive/ 中 26 個舊檔案全部從混合命名統一為 `kebab-case` + 日期前綴

---

## 3. 導入 Spec-Kit 開發規範

### 背景
專案中已存在 `spec-kit/` 目錄（GitHub 的 Spec-Driven Development 框架）。經評估後決定**選擇性採用**——不導入完整 SDD 流程，僅取用最有價值的兩個部分。

### 評估結論

| spec-kit 功能 | 採用？ | 理由 |
|---------------|--------|------|
| `constitution` — 專案公約 | ✅ 採用 | 解決多 LLM 風格不一致的根本問題 |
| `specify` + `plan` — 功能規格 | ✅ P2 功能採用 | 大型功能先定規格再實作 |
| `clarify` — 規格澄清 | ❌ 暫不 | 目前需求來源單一 |
| `tasks` — 任務拆解 | ❌ 暫不 | 功能規模不大，plan 中已含 phases |
| `analyze` — 一致性檢查 | ❌ 暫不 | 產物數量少 |
| `implement` — 自動實作 | ❌ 暫不 | 偏好手動控制 |

### 建立的 Constitution（v1.0.0）

檔案：`.specify/memory/constitution.md`

7 項核心原則：

1. **Config-Driven, Zero Hardcode** — 所有可變參數從 config 讀取，嚴禁硬編碼
2. **Consistent API Contract** — 統一 `{status, data}` 回應格式，錯誤用 `HTTPException`
3. **Python Naming & Style** — `snake_case` 函式 / `PascalCase` 類別 / 用 `logger` 不用 `print`
4. **Frontend Conventions** — `camelCase` JS / `addEventListener` 不用 inline onclick
5. **Documentation as Code** — `kebab-case.md`、子目錄分類、同步更新索引
6. **Single Source of Truth** — 每類資訊一個權威來源，禁止多處重複定義
7. **Graceful Degradation** — 異常時回退而非 crash，現場活動可靠性最優先

另含 Technology Stack 限制（禁止引入前端框架、ORM、打包工具）和 Development Workflow 規則（P2+ 先寫 spec，P0/P1 直接修但需記錄）。

---

## 4. P2 功能規格撰寫

為兩個 P2 大型功能建立了完整的 spec + plan：

### 001-mobile-admin-ui

```
specs/001-mobile-admin-ui/
├── spec.md   — 3 個 User Story、10 個 FR、5 個 SC
└── plan.md   — CSS Media Queries + JS LayoutManager 方案
```

- **方案**: 單一檔案改造 `admin.html`，用 CSS Media Queries 實現四個斷點（Mobile ≤480px / Phone-L ≤767px / Tablet ≥768px / Desktop ≥1024px）
- **關鍵設計**: 手機端單欄 + 底部導覽、全螢幕照片預覽 overlay、觸控手勢滑動切換
- **預估**: 2.5 天、零後端修改

### 002-watermark-advanced

```
specs/002-watermark-advanced/
├── spec.md   — 3 個 User Story、9 個 FR、4 個 SC
└── plan.md   — 後端字型 API + Canvas 預覽 + 拖拽定位
```

- **方案**: 新增 `GET /api/available-fonts` API、前端 Canvas 即時預覽、mousedown/move/up 拖拽定位
- **關鍵設計**: 字型列表由後端掃描系統字型並驗證 CJK 支援；位置用百分比座標適應不同照片尺寸
- **預估**: 2.5 天

---

## 📁 今日新增/修改的檔案

### 新增
| 檔案 | 說明 |
|------|------|
| `.specify/memory/constitution.md` | 專案公約 v1.0.0 |
| `specs/001-mobile-admin-ui/spec.md` | Mobile Admin UI 功能規格 |
| `specs/001-mobile-admin-ui/plan.md` | Mobile Admin UI 技術方案 |
| `specs/002-watermark-advanced/spec.md` | Watermark 進階功能規格 |
| `specs/002-watermark-advanced/plan.md` | Watermark 進階技術方案 |
| `docs/dev/plans/2026-02-11-development-plan.md` | 15 項待開發功能的完整開發計劃 |
| `docs/dev/logs/2026-02-11-spec-kit-and-docs-restructure.md` | 本日誌 |

### 移動+重新命名（git mv，保留歷史）
共 36 個檔案從 `docs/` 平鋪結構移入 `docs/guides/`、`docs/reference/`、`docs/dev/`、`docs/archive/` 並統一為 `kebab-case.md`。

### 修改（更新引用路徑）
- `README.md`（根目錄）
- `docs/README.md`
- `docs/guides/troubleshooting.md`
- `docs/reference/architecture.md`
- `docs/reference/project-status.md`
- `docs/dev/changelog.md`

---

## 5. spec-kit 原始碼清理

### 問題
導入 Spec-Kit 規範時，將 spec-kit 的**完整 GitHub 倉庫**（`https://github.com/github/spec-kit`）clone 到了專案根目錄 `spec-kit/`。

檢查後發現以下問題：

| 指標 | 數值 |
|------|------|
| 大小 | 8.1 MB |
| 檔案數 | 102 個（含 `.git`、`.github/workflows`、`src/` Python CLI、`media/` 圖片等） |
| 被本專案 git 追蹤 | 0 個檔案 |
| 被 .gitignore 排除 | 沒有 |

### 為什麼不放 Archive？

`docs/archive/` 是存放**本專案自己的**歷史文件。`spec-kit/` 是第三方工具的完整原始碼倉庫，性質不同——它不是我們寫的、也不是我們專案的產物。此外，它含有自己的 `.git` 目錄，嵌套在本專案的 git repo 中會造成版本控制混亂。

### 決策：直接刪除

我們已經從 spec-kit 提取了所有需要的價值：
- **Constitution 格式** → 已建立 `.specify/memory/constitution.md`
- **Spec / Plan template** → 已建立 `specs/001-*/`、`specs/002-*/`
- **SDD 流程理解** → 已記錄在本日誌的「導入 Spec-Kit 開發規範」章節

未來如需重新參考，可從 `https://github.com/github/spec-kit` 隨時取得。

### 執行
- 刪除 `spec-kit/` 整個目錄
- 在 `.gitignore` 中加入 `spec-kit/`，防止未來意外再次加入

---

## 📅 下一步

| 優先級 | 項目 | 依據 |
|--------|------|------|
| P0 | `R2_PATH_PREFIX` 動態化 | Constitution 原則 I 要求 |
| P0 | Hero Banner UI Bugs 修復 | 2026-02-06 日誌殘留問題 |
| P0 | Cloudflare Pages 部署確認 | 觀眾端仍可能顯示舊版 |
| P1 | Batch Publish 獨立參數 | 開發計劃 P1-4 |
| P1 | EXIF Metadata 保留 | 開發計劃 P1-5 |
| P2 | Mobile Admin UI | 已有 spec + plan，待實作 |
| P2 | Watermark 進階 | 已有 spec + plan，待實作 |
