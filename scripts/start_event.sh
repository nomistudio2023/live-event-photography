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

# 防止 Python 生成 bytecode
export PYTHONDONTWRITEBYTECODE=1
# 防止 macOS 生成 ._ 文件
export COPYFILE_DISABLE=1

# 清理現有的隱藏文件 (._*)
echo "🧹 清理臨時文件..."
find . -name "._*" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# 檢查端口是否被占用，如果是則強制殺死
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 被占用，正在清理舊進程..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# 啟動 Admin 後台 (背景執行)
echo "🖥️  啟動 Admin 後台..."
python3 server.py &
SERVER_PID=$!
echo "   PID: $SERVER_PID"
echo "   URL: http://localhost:8000"
echo ""

# 等待 server 啟動
sleep 2

# 自動開啟瀏覽器
echo "🌐 開啟管理後台..."
open "http://localhost:8000"

# 啟動 R2 同步腳本 (前景執行，方便看 log)
echo "☁️  啟動 R2 同步腳本..."
echo ""
python3 sync_to_r2.py

# 當同步腳本被中斷時，也關閉 server
echo ""
echo "🛑 正在關閉 Admin 後台 (PID: $SERVER_PID)..."
kill $SERVER_PID 2>/dev/null

echo "👋 所有服務已停止"
