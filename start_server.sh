#!/bin/bash
#
# 啟動 FastAPI Admin 後台
# 此腳本用於 Mac App 啟動器
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 設定終端標題
echo -e "\033]0;Live Event Photo - Server\007"

echo "================================================"
echo "🖥️  Live Event Photography - Admin Server"
echo "================================================"
echo ""
echo "📂 工作目錄: $SCRIPT_DIR"
echo "🌐 URL: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服務器"
echo "================================================"
echo ""

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3，請先安裝"
    read -p "按 Enter 關閉..."
    exit 1
fi

# 檢查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  端口 8000 已被占用"
    echo "正在停止舊的服務器..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 啟動服務器
python3 server.py

# 如果服務器意外退出，保持終端開啟以便查看錯誤
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 服務器異常退出"
    read -p "按 Enter 關閉..."
fi
