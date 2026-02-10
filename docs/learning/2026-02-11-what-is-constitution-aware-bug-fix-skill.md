# 從 Bug 修復過程中提煉 LLM Agent Skill

**日期**: 2026-02-11
**類型**: 問答紀錄 — LLM 工作流程與 Skill 概念
**情境**: 完成 R2 path prefix 硬編碼修復（2 個 bug、4 個檔案）後，回顧工作流程

---

## 問：今天的開發過程，可以被定義為一種 LLM 運作用的 Skill 嗎？

### 背景

今天的修復工作涉及：
1. 驗證 `index.html` 中 `2026-01-20` 硬編碼存在
2. 追蹤資料流橫跨 4 個檔案（config → server.py → sync_to_r2.py → index.html）
3. 對照 Constitution 設計修復方案
4. 實作過程中發現 bootstrap 失敗導致空白頁的 cascade bug
5. 用 grep 驗證零殘留、lint 檢查
6. 撰寫開發日誌

### 回答：是的，這構成一個可複用的結構化 Skill

將工作流程拆解後，發現我遵循了一個**隱含的 8 步驟結構**：

| 步驟 | 名稱 | 動作 | 今日實例 |
|------|------|------|---------|
| 1 | **Verify** | 不盲信 bug report，讀實際程式碼確認 | 讀 index.html L493-495 確認硬編碼 |
| 2 | **Trace** | 追蹤資料流，找出所有相關檔案 | config → server → sync → frontend |
| 3 | **Constrain** | 對照 constitution 確認修復必須滿足的原則 | Principle I (Config-Driven)、VII (Graceful Degradation) |
| 4 | **Design** | 設計符合約束的方案（解決根因，非症狀） | Bootstrap 機制解決 chicken-and-egg |
| 5 | **Implement** | 依依賴順序修改所有檔案 | config → server → sync → frontend |
| 6 | **Cascade-check** | 檢查修復本身是否引入新邊界問題 | 發現 bootstrap 失敗 → 空白頁問題 |
| 7 | **Validate** | grep 殘留問題 + lint 檢查 | 確認零 `2026-01-20` 殘留 |
| 8 | **Document** | 記錄根因、方案、決策理由 | 建立開發日誌 |

### 這個 Skill 的命名

**Constitution-Aware Bug Remediation**（公約感知的 Bug 修復）

核心特徵：
- **不是**單純的 "fix a bug"
- **是**帶有項目約束意識的結構化修復工作流
- 強制在設計修復方案**之前**讀取 constitution
- 主動檢查修復是否引入 cascade bug

---

## 問：跟已有的 Skill 有什麼差異？

### 與既有 Skill 的比較

| 既有 Skill | 重疊部分 | 差異 |
|-----------|---------|------|
| `systematic-debugging` | 步驟 1-2（驗證、追蹤） | 不涵蓋 constitution 約束和 cascade check |
| `verification-before-completion` | 步驟 7（驗證） | 只管最後驗證，不管全流程 |
| `code-reviewer` | 步驟 6（發現問題） | Review 只讀不改，且缺少修復設計 |
| `test-driven-development` | 步驟 7（驗證） | 面向新功能，非 bug 修復 |

**結論**：這個 Skill 填補了從「收到 bug report」到「修復完成並記錄」的完整閉環，特別是**步驟 3（Constitution 約束）和步驟 6（Cascade-check）**是其他 Skill 沒有涵蓋的。

---

## 問：為什麼值得形式化為 SKILL.md？

### 三個關鍵理由

1. **多 LLM 迭代的一致性問題**
   - 不同 LLM 修 bug 的風格差異大
   - 有的只改一個檔案就交差
   - 有的不查 constitution 就硬改
   - Skill 強制統一流程

2. **Constitution 需要被自動引用**
   - 公約存在但需要被「自動讀取」
   - 不能依賴 LLM「碰巧知道」或「碰巧想到」
   - Phase 3 強制讀取 `.specify/memory/constitution.md`

3. **Cascade bug 風險在多檔案耦合架構中特別高**
   - config → server → sync → frontend 的改動鏈
   - 局部修復容易引入新問題
   - Phase 6 強制檢查

---

## 產出

基於這次討論，建立了 Project-level Skill：

```
.cursor/skills/constitution-aware-bug-fix/SKILL.md
```

放在 Project 層級（而非個人 `~/.cursor/skills/`），因為此 Skill 引用專案特定的 constitution 檔案路徑。

---

## 學到的概念

| 概念 | 說明 |
|------|------|
| **Agent Skill** | 一組結構化的指令，讓 LLM 在特定情境下遵循固定工作流程 |
| **SKILL.md** | Cursor 格式的 Skill 定義檔，包含 YAML frontmatter（name + description）和 markdown body |
| **Skill Description** | 決定 LLM 何時自動觸發此 Skill 的關鍵欄位，需包含 WHAT 和 WHEN |
| **Project vs Personal Skill** | `.cursor/skills/`（隨專案走）vs `~/.cursor/skills/`（跨專案個人使用） |
| **Cascade-check** | 修復完成後主動檢查是否引入新的邊界問題 — 在多檔案耦合架構中尤其重要 |
| **Constitution as Constraint** | 將程式風格/架構原則形式化為公約，讓 Skill 能強制 LLM 在修改前讀取並遵守 |
