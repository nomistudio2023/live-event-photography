from PIL import Image, ImageDraw, ImageFont
import os

# 確保資料夾存在
os.makedirs('assets', exist_ok=True)

# 建立一張 800x200 的透明背景圖片
width = 800
height = 200
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

text = "LIVE EVENT 2026"
font = None

# 嘗試載入系統字體 (Mac)
try:
    # 嘗試較粗的字體，更有 Logo 感
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 100)
except:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
    except:
        print("未找到系統字體，使用預設字體")
        font = ImageFont.load_default()

# 計算文字位置以置中 (簡單估算)
# 畫上文字：白色字體 + 黑色陰影/描邊，確保在亮或暗的照片上都看得到
x, y = 50, 40
stroke_width = 4

# 畫描邊 (模擬)
draw.text((x, y), text, font=font, fill=(0, 0, 0, 180), stroke_width=stroke_width, stroke_fill=(0, 0, 0, 255))
# 畫本體
draw.text((x, y), text, font=font, fill=(255, 255, 255, 230))

output_path = 'assets/watermark.png'
img.save(output_path)
print(f"✅ 測試浮水印已產生: {output_path}")
