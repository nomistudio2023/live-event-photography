# 禁用 macOS 自動產生隱藏文件的方法

## 🎯 方法 1: 在 Python 代碼中禁用（推薦）✅

這是最有效的方法，在複製文件時禁用資源分叉。

### 修改 server.py

在文件開頭添加環境變數設置：

```python
import os
# 禁用 macOS 資源分叉（._ 文件）
os.environ['COPYFILE_DISABLE'] = '1'
```

這會影響所有使用 `shutil.copy` 和 `shutil.copy2` 的操作。

---

## 🎯 方法 2: 使用 dot_clean 命令

定期清理隱藏文件：

```bash
# 清理特定資料夾
dot_clean /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web

# 清理所有資料夾
dot_clean -m /Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/
```

**注意**：`dot_clean` 會合併隱藏文件到主文件，然後刪除隱藏文件。

---

## 🎯 方法 3: 修改複製命令

在複製文件時使用 `cp -X` 選項：

```bash
cp -X source.jpg destination.jpg
```

`-X` 選項會排除擴展屬性（extended attributes），從而避免產生 `._` 文件。

---

## 🎯 方法 4: 使用 rsync 替代複製

rsync 可以排除隱藏文件：

```bash
rsync -av --exclude='._*' --exclude='.DS_Store' source/ destination/
```

---

## 🎯 方法 5: 在 Terminal 中設置環境變數（全局）

在 `~/.zshrc` 或 `~/.bash_profile` 中添加：

```bash
export COPYFILE_DISABLE=1
```

然後重新載入：
```bash
source ~/.zshrc
```

---

## ✅ 推薦方案：修改 server.py

讓我為您修改 server.py，在文件開頭添加環境變數設置。
