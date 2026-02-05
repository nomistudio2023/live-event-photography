#!/bin/bash
# Live Event Photography - 專案狀態檢查腳本

echo "🔍 Live Event Photography - 專案狀態檢查"
echo "=========================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查核心檔案
echo "📁 檢查核心檔案..."
files=(
    "server.py"
    "sync_to_r2.py"
    "r2_manage.py"
    "start_event.sh"
    "templates/admin.html"
    "index.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
    fi
done

echo ""

# 檢查目錄
echo "📂 檢查目錄結構..."
dirs=(
    "photos_buffer"
    "photos_web"
    "photos_archive"
    "photos_trash"
    "templates"
    "assets"
    "functions/photo"
)

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} $dir ($count 個檔案)"
    else
        echo -e "${YELLOW}⚠${NC} $dir (不存在)"
    fi
done

echo ""

# 檢查 Cloudflare Functions
echo "☁️ 檢查 Cloudflare Functions..."
if [ -f "functions/photo/[[path]].js" ]; then
    echo -e "${GREEN}✓${NC} Cloudflare Function 已存在"
else
    echo -e "${YELLOW}⚠${NC} Cloudflare Function 不存在（已創建模板）"
fi

# 檢查 wrangler.toml
if [ -f "wrangler.toml" ]; then
    echo -e "${GREEN}✓${NC} wrangler.toml 已存在"
    # 檢查 R2 綁定
    if grep -q "GALLERY" wrangler.toml; then
        echo -e "${GREEN}✓${NC} R2 綁定 (GALLERY) 已配置"
    else
        echo -e "${YELLOW}⚠${NC} R2 綁定未找到"
    fi
else
    echo -e "${YELLOW}⚠${NC} wrangler.toml 不存在（需要配置 Cloudflare Pages）"
fi

echo ""

# 檢查 Python 依賴
echo "🐍 檢查 Python 依賴..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt 存在"
    if command -v pip3 &> /dev/null; then
        echo "   檢查已安裝的套件..."
        while IFS= read -r line; do
            if [[ ! "$line" =~ ^# ]] && [[ -n "$line" ]]; then
                package=$(echo "$line" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
                if pip3 show "$package" &> /dev/null; then
                    echo -e "   ${GREEN}✓${NC} $package"
                else
                    echo -e "   ${RED}✗${NC} $package (未安裝)"
                fi
            fi
        done < requirements.txt
    else
        echo -e "${YELLOW}⚠${NC} pip3 未找到，無法檢查依賴"
    fi
else
    echo -e "${RED}✗${NC} requirements.txt 不存在"
fi

echo ""

# 檢查 rclone 配置
echo "🔄 檢查 rclone 配置..."
if command -v rclone &> /dev/null; then
    echo -e "${GREEN}✓${NC} rclone 已安裝"
    if rclone config show r2livegallery &> /dev/null; then
        echo -e "${GREEN}✓${NC} rclone 遠端 'r2livegallery' 已配置"
    else
        echo -e "${YELLOW}⚠${NC} rclone 遠端 'r2livegallery' 未配置"
    fi
else
    echo -e "${RED}✗${NC} rclone 未安裝"
fi

echo ""

# 檢查照片統計
echo "📸 照片統計..."
if [ -d "photos_buffer" ]; then
    buffer_count=$(find photos_buffer -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l | tr -d ' ')
    echo "   Buffer: $buffer_count 張"
fi

if [ -d "photos_web" ]; then
    web_count=$(find photos_web -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l | tr -d ' ')
    echo "   Web (已發布): $web_count 張"
    
    if [ -f "photos_web/manifest.json" ]; then
        echo -e "   ${GREEN}✓${NC} manifest.json 存在"
    else
        echo -e "   ${YELLOW}⚠${NC} manifest.json 不存在"
    fi
fi

echo ""
echo "=========================================="
echo "✅ 檢查完成！"
echo ""
echo "📋 後續步驟："
echo "   1. 查看 DEVELOPMENT_ROADMAP.md 了解開發計劃"
echo "   2. 確認 Cloudflare Functions 部署狀態"
echo "   3. 測試 R2 同步功能"
echo ""
