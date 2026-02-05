#!/bin/bash
# 定期清理隱藏文件的腳本
# 使用 macOS 的 dot_clean 命令

WEB_FOLDER="/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_web"
BUFFER_FOLDER="/Volumes/詠松-2Tssd/2026-live-event-photograghy-test-folder/photos_buffer"

echo "🧹 清理隱藏文件..."

if [ -d "$WEB_FOLDER" ]; then
    echo "清理 Web 資料夾..."
    dot_clean -m "$WEB_FOLDER"
    echo "✅ Web 資料夾已清理"
fi

if [ -d "$BUFFER_FOLDER" ]; then
    echo "清理 Buffer 資料夾..."
    dot_clean -m "$BUFFER_FOLDER"
    echo "✅ Buffer 資料夾已清理"
fi

echo "✅ 清理完成！"
