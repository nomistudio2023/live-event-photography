#!/bin/bash
#
# 活動攝影一鍵啟動腳本
# 同時啟動 Admin 後台 + R2 自動同步
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "================================================"
echo "🎬 Live Event Photography - 活動模式啟動"
echo "================================================"
echo ""

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3，請先安裝"
    exit 1
fi

# 檢查 rclone
if ! command -v rclone &> /dev/null; then
    echo "❌ 找不到 rclone，請先安裝: brew install rclone"
    exit 1
fi

echo "📂 工作目錄: $PROJECT_DIR"
echo ""

# 啟動 Admin 後台 (背景執行)
echo "🖥️  啟動 Admin 後台..."
python3 server.py &
SERVER_PID=$!
echo "   PID: $SERVER_PID"
echo "   URL: http://localhost:8000"
echo ""

# 等待 server 啟動
sleep 2

# 啟動 R2 同步腳本 (前景執行，方便看 log)
echo "☁️  啟動 R2 同步腳本..."
echo ""
python3 sync_to_r2.py

# 當同步腳本被中斷時，也關閉 server
echo ""
echo "🛑 正在關閉 Admin 後台 (PID: $SERVER_PID)..."
kill $SERVER_PID 2>/dev/null

echo "👋 所有服務已停止"
