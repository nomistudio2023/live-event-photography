import sys
import time
import os
import logging
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageOps

# ================= 設定區 =================
# 設定來源資料夾 (相機/Lightroom 輸出的原始大圖)
SOURCE_FOLDER = r"./photos_original"  # 範例：Mac 請改為 '/Users/name/Photos/Original'
# 設定目標資料夾 (網頁要用的壓縮圖)
DEST_FOLDER = r"./photos_web"        # 範例：Mac 請改為 '/Users/name/Photos/Web'

# 壓縮設定
MAX_SIZE = (1600, 1600)  # 設定長邊最大像素 (1600px 足夠手機與一般螢幕預覽)
JPEG_QUALITY = 80        # 壓縮品質 (1-100)，80 是畫質與檔案大小的最佳平衡點
# =========================================

class ImageCompressorHandler(FileSystemEventHandler):
    """處理檔案建立事件"""
    def on_created(self, event):
        if event.is_directory:
            return

        # 檢查是否為圖片檔 (可依需求增加 png, jpeg)
        filename = event.src_path
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"📷 偵測到新照片: {os.path.basename(filename)}")
            self.process_image(filename)

    def process_image(self, source_path):
        """等待檔案寫入完成並執行壓縮"""
        # 簡單的重試機制，防止讀取到正在寫入中的檔案
        retries = 5
        while retries > 0:
            try:
                # 嘗試開啟並處理圖片
                with Image.open(source_path) as img:
                    # 1. 處理 EXIF 旋轉 (很多相機直拍照片若不處理，上網頁會倒過來)
                    img = ImageOps.exif_transpose(img)
                    
                    # 2. 轉換為 RGB (防止 PNG 透明圖層存成 JPG 報錯)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    # 3. 縮圖 (保持比例)
                    img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                    
                    # 4. 建構輸出路徑
                    base_name = os.path.basename(source_path)
                    name, ext = os.path.splitext(base_name)
                    # 輸出檔名統一轉為 .jpg
                    output_path = os.path.join(DEST_FOLDER, name + ".jpg")

                    # 5. 存檔
                    img.save(output_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
                    
                    file_size_kb = os.path.getsize(output_path) / 1024
                    print(f"✅ 壓縮完成: {name}.jpg -> {file_size_kb:.1f} KB")

                    # 6. 更新清單檔案 (Manifest)
                    self.update_manifest()
                    return # 成功則退出函數

            except OSError:
                # 檔案可能被鎖定或尚未寫入完成
                time.sleep(1) # 等待 1 秒
                retries -= 1
            except Exception as e:
                print(f"❌ 處理失敗: {e}")
                return

        print(f"❌ 放棄處理 (檔案佔用過久): {os.path.basename(source_path)}")

    def update_manifest(self):
        """更新照片清單 JSON 檔案，供網頁端讀取"""
        try:
            # 取得目標資料夾內所有 jpg 檔案
            files = [f for f in os.listdir(DEST_FOLDER) if f.lower().endswith(('.jpg', '.jpeg'))]
            
            # 依照修改時間排序 (最新的在最前面)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(DEST_FOLDER, x)), reverse=True)
            
            # 寫入 JSON
            manifest_path = os.path.join(DEST_FOLDER, 'manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(files, f, ensure_ascii=False, indent=2)
            
            print(f"📄 清單已更新: {len(files)} 張照片")
        except Exception as e:
            print(f"⚠️ 更新清單失敗: {e}")

def main():
    # 確保資料夾存在
    if not os.path.exists(SOURCE_FOLDER):
        os.makedirs(SOURCE_FOLDER)
        print(f"建立來源資料夾: {SOURCE_FOLDER}")
    if not os.path.exists(DEST_FOLDER):
        os.makedirs(DEST_FOLDER)
        print(f"建立目標資料夾: {DEST_FOLDER}")

    # 設定監控
    event_handler = ImageCompressorHandler()
    observer = Observer()
    observer.schedule(event_handler, SOURCE_FOLDER, recursive=False)
    observer.start()

    print(f"👀 正在監控: {SOURCE_FOLDER}")
    print(f"🚀 輸出位置: {DEST_FOLDER}")
    print("按 Ctrl+C 停止腳本...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
