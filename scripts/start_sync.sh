#!/bin/bash
#
# 啟動 R2 自動同步腳本
# 此腳本用於 Mac App 啟動器
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# 設定終端標題
echo -e "\033]0;Live Event Photo - Sync\007"

echo "================================================"
echo "☁️  Live Event Photography - R2 Sync"
echo "================================================"
echo ""
echo "📂 工作目錄: $PROJECT_DIR"
echo "📸 監控資料夾: photos_web/"
echo ""
echo "按 Ctrl+C 停止同步"
echo "================================================"
echo ""

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3，請先安裝"
    read -p "按 Enter 關閉..."
    exit 1
fi

# 檢查 rclone
if ! command -v rclone &> /dev/null; then
    echo "❌ 找不到 rclone，請先安裝: brew install rclone"
    read -p "按 Enter 關閉..."
    exit 1
fi

# 檢查 rclone 配置
if ! rclone config show r2livegallery &> /dev/null; then
    echo "⚠️  rclone 遠端 'r2livegallery' 未配置"
    echo "請先執行: rclone config"
    read -p "按 Enter 關閉..."
    exit 1
fi

# 啟動同步腳本
python3 sync_to_r2.py

# 如果同步腳本意外退出，保持終端開啟以便查看錯誤
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 同步腳本異常退出"
    read -p "按 Enter 關閉..."
fi
