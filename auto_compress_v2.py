import sys
import time
import os
import json
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

# 預設設定，如果 config.json 讀取失敗會用這組
DEFAULT_CONFIG = {
    "watch_folder": "./photos_original",
    "output_folder": "./photos_web",
    "max_size": 1600,
    "jpeg_quality": 85,
    "processing": {
        "sharpen": True,
        "progressive": True,
        "watermark": {
            "enabled": False
        },
        "frame": {
            "enabled": False
        }
    }
}

class ImageProcessor:
    def __init__(self, config):
        self.config = config
        
    def load_watermark_assets(self):
        """預先載入浮水印或外框圖片以提升效能"""
        self.watermark_img = None
        self.frame_img = None
        
        proc_config = self.config.get('processing', {})
        
        # 載入浮水印
        wm_config = proc_config.get('watermark', {})
        if wm_config.get('enabled') and os.path.exists(wm_config.get('image_path', '')):
            try:
                self.watermark_img = Image.open(wm_config['image_path']).convert("RGBA")
                print("✅ 浮水印素材載入成功")
            except Exception as e:
                print(f"⚠️ 浮水印載入失敗: {e}")

        # 載入外框
        frame_config = proc_config.get('frame', {})
        if frame_config.get('enabled') and os.path.exists(frame_config.get('image_path', '')):
            try:
                self.frame_img = Image.open(frame_config['image_path']).convert("RGBA")
                print("✅ 外框素材載入成功")
            except Exception as e:
                print(f"⚠️ 外框載入失敗: {e}")

    def process_image_pipeline(self, img_path):
        """影像處理核心流水線"""
        try:
            with Image.open(img_path) as img:
                # 1. 基礎處理 (EXIF 轉向 & RGB 轉換)
                img = ImageOps.exif_transpose(img)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                # 取得設定
                proc_config = self.config.get('processing', {})
                max_size = self.config.get('max_size', 1600)
                
                # 2. 智慧銳利化 (Smart Sharpening) - 在縮圖前先做一次輕微銳化效果更好
                if proc_config.get('sharpen'):
                    # 簡單的 Unsharp Mask
                    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

                # 3. 縮圖邏輯 (Resize)
                # 如果有外框 (Frame)，縮圖策略會不同
                if self.frame_img and proc_config['frame']['enabled']:
                    img = self._apply_frame(img, max_size)
                else:
                    # 一般縮圖
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                # 4. 浮水印疊加 (Watermark)
                if self.watermark_img and proc_config['watermark']['enabled']:
                    img = self._apply_watermark(img)

                return img
                
        except Exception as e:
            print(f"❌ 影像處理錯誤 ({os.path.basename(img_path)}): {e}")
            return None

    def _apply_frame(self, img, target_size):
        """套用外框邏輯"""
        mode = self.config['processing']['frame'].get('mode', 'cover') # cover or contain
        frame = self.frame_img
        
        # 外框通常就是最終輸出的尺寸基準
        # 這裡假設外框要縮放到 target_size (例如長邊 1600)
        # 但為了保持外框解析度，我們先計算外框的縮放比例
        frame_ratio = target_size / max(frame.size)
        new_frame_size = (int(frame.width * frame_ratio), int(frame.height * frame_ratio))
        frame_resized = frame.resize(new_frame_size, Image.Resampling.LANCZOS)
        
        final_canvas = Image.new("RGB", frame_resized.size, (255, 255, 255))
        
        if mode == 'cover':
            # 滿版裁切 (Center Crop)
            img_ratio = max(new_frame_size) / min(img.size) # 用最小邊去配合最大框，確保填滿
            # 實際上比較複雜，簡單用 ImageOps.fit
            img_filled = ImageOps.fit(img, new_frame_size, method=Image.Resampling.LANCZOS)
            final_canvas.paste(img_filled, (0, 0))
            
        elif mode == 'contain':
            # 完整縮放 (Fit)
            img_copy = img.copy()
            img_copy.thumbnail(new_frame_size, Image.Resampling.LANCZOS)
            # 置中貼上
            pos_x = (new_frame_size[0] - img_copy.width) // 2
            pos_y = (new_frame_size[1] - img_copy.height) // 2
            final_canvas.paste(img_copy, (pos_x, pos_y))
            
        # 疊上外框 (Frame 必須是 PNG 透明圖層)
        final_canvas.paste(frame_resized, (0, 0), frame_resized)
        return final_canvas

    def _apply_watermark(self, img):
        """套用浮水印邏輯"""
        wm_config = self.config['processing']['watermark']
        wm = self.watermark_img.copy()
        
        # 計算浮水印大小 (相對於主圖的百分比)
        scale = wm_config.get('scale_percentage', 20) / 100
        target_wm_width = int(min(img.size) * scale)
        wm_ratio = target_wm_width / wm.width
        new_wm_size = (int(wm.width * wm_ratio), int(wm.height * wm_ratio))
        
        wm = wm.resize(new_wm_size, Image.Resampling.LANCZOS)
        
        # 調整透明度
        opacity = wm_config.get('opacity', 0.8)
        if opacity < 1.0:
            alpha = wm.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            wm.putalpha(alpha)
            
        # 計算位置
        margin = wm_config.get('margin', 30)
        pos_config = wm_config.get('position', 'bottom-right')
        
        x, y = 0, 0
        if pos_config == 'bottom-right':
            x = img.width - wm.width - margin
            y = img.height - wm.height - margin
        elif pos_config == 'bottom-left':
            x = margin
            y = img.height - wm.height - margin
        elif pos_config == 'top-right':
            x = img.width - wm.width - margin
            y = margin
        elif pos_config == 'center':
            x = (img.width - wm.width) // 2
            y = (img.height - wm.height) // 2
            
        # 確保不會貼到外面去
        x = max(0, min(x, img.width - wm.width))
        y = max(0, min(y, img.height - wm.height))
        
        # 由於要保留底圖，且浮水印有透明度，需將主圖轉為 RGBA 疊合後再轉回 RGB
        img_rgba = img.convert("RGBA")
        img_rgba.alpha_composite(wm, (x, y))
        return img_rgba.convert("RGB")


class Watcher(FileSystemEventHandler):
    def __init__(self, processor, output_folder, jpeg_quality, progressive):
        self.processor = processor
        self.output_folder = output_folder
        self.jpeg_quality = jpeg_quality
        self.progressive = progressive

    def on_created(self, event):
        if event.is_directory: return
        filename = event.src_path
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"📷 偵測到: {os.path.basename(filename)} - 處理中...")
            
            # 給相機一點寫入時間
            time.sleep(1.5)
            
            processed_img = self.processor.process_image_pipeline(filename)
            
            if processed_img:
                self.save_image(processed_img, filename)
                self.update_manifest()

    def save_image(self, img, original_path):
        base_name = os.path.basename(original_path)
        name, _ = os.path.splitext(base_name)
        output_path = os.path.join(self.output_folder, name + ".jpg")
        
        try:
            img.save(
                output_path, 
                "JPEG", 
                quality=self.jpeg_quality, 
                optimize=True, 
                progressive=self.progressive
            )
            print(f"✅ 完成: {os.path.basename(output_path)}")
        except Exception as e:
            print(f"❌ 存檔失敗: {e}")

    def update_manifest(self):
        try:
            files = [f for f in os.listdir(self.output_folder) if f.lower().endswith(('.jpg', '.jpeg'))]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_folder, x)), reverse=True)
            manifest_path = os.path.join(self.output_folder, 'manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(files, f, ensure_ascii=False, indent=2)
        except:
            pass

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

def main():
    config = load_config()
    source_folder = config['watch_folder']
    dest_folder = config['output_folder']
    
    if not os.path.exists(source_folder): os.makedirs(source_folder)
    if not os.path.exists(dest_folder): os.makedirs(dest_folder)
    
    processor = ImageProcessor(config)
    processor.load_watermark_assets() # 預先載入圖片
    
    event_handler = Watcher(
        processor, 
        dest_folder, 
        config['jpeg_quality'],
        config['processing']['progressive']
    )
    
    observer = Observer()
    observer.schedule(event_handler, source_folder, recursive=False)
    observer.start()
    
    print(f"🚀 V2 引擎啟動 | 來源: {source_folder} -> 輸出: {dest_folder}")
    print(f"🔧 功能啟用: 銳利化={config['processing']['sharpen']}, 漸進載入={config['processing']['progressive']}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
