#!/bin/bash
#
# 更新 Mac App 中的 AppleScript
# 編譯 launcher.applescript 並替換 app bundle 中的 main.scpt
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_PATH="dist/Live Event Photo.app"
SCRIPT_SOURCE="launcher.applescript"
SCRIPT_DEST="${APP_PATH}/Contents/Resources/Scripts/main.scpt"

echo "================================================"
echo "🔧 更新 Mac App AppleScript"
echo "================================================"
echo ""

# 檢查 app 是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 找不到 Mac App: $APP_PATH"
    echo ""
    echo "請先執行 build_mac_app.sh 構建 app"
    exit 1
fi

# 檢查源文件是否存在
if [ ! -f "$SCRIPT_SOURCE" ]; then
    echo "❌ 找不到源文件: $SCRIPT_SOURCE"
    exit 1
fi

# 編譯 AppleScript
echo "📝 編譯 AppleScript..."
osacompile -o "$SCRIPT_DEST" "$SCRIPT_SOURCE"

if [ $? -eq 0 ]; then
    echo "✅ AppleScript 已更新: $SCRIPT_DEST"
    echo ""
    echo "📋 更新內容："
    echo "   - 使用 shell 腳本啟動（避免 Apple Events 權限問題）"
    echo "   - 自動啟動 server.py 和 sync_to_r2.py"
    echo ""
    echo "⚠️  注意：如果 app 已經簽名，更新後可能需要重新簽名"
else
    echo "❌ 編譯失敗"
    exit 1
fi
