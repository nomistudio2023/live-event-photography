#!/usr/bin/env python3
"""
R2 自動同步腳本 - Live Event Photography
監控 photos_web 資料夾，自動同步到 Cloudflare R2

使用方式：
    python3 sync_to_r2.py

按 Ctrl+C 停止
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 禁用 macOS 資源分叉（._ 文件）的產生
os.environ['COPYFILE_DISABLE'] = '1'

# ============ 配置區 ============
# 載入 config.json 以取得動態資料夾路徑
def load_config():
    """Load config from config.json, fallback to default"""
    config_file = Path(__file__).parent / "config" / "config.json"
    default_web_folder = Path(__file__).parent / "photos_web"
    
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                web_folder = config.get("web_folder", "./photos_web")
                # Convert relative path to absolute
                if web_folder.startswith("./"):
                    web_folder = str(Path(__file__).parent / web_folder[2:])
                elif not os.path.isabs(web_folder):
                    web_folder = str(Path(__file__).parent / web_folder)
                return Path(web_folder)
        except Exception as e:
            print(f"⚠️  無法讀取 config.json: {e}")
    
    return default_web_folder

# 本地照片資料夾（從 config.json 讀取）
LOCAL_PHOTOS_DIR = load_config()
print(f"📂 使用資料夾: {LOCAL_PHOTOS_DIR}")

# rclone 遠端名稱 (從 rclone config 取得)
RCLONE_REMOTE = "r2livegallery"

# R2 bucket 名稱
BUCKET_NAME = "nomilivegallery"

# R2 中的路徑前綴 (用於組織不同活動)
R2_PATH_PREFIX = "2026-01-20"

# 支援的照片格式
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# 檢查間隔 (秒)
CHECK_INTERVAL = 3

# 安全模式：只新增照片，不自動刪除 R2 上的照片
# 設為 False 可啟用刪除功能（謹慎使用）
SAFE_MODE = True
# ================================


def get_local_photos():
    """取得本地照片列表"""
    if not LOCAL_PHOTOS_DIR.exists():
        return set()

    photos = {
        f.name for f in LOCAL_PHOTOS_DIR.iterdir()
        if f.is_file() and not f.name.startswith('.') and f.suffix.lower() in PHOTO_EXTENSIONS
    }
    return photos


def get_r2_photos():
    """取得 R2 上的照片列表"""
    try:
        result = subprocess.run(
            ["rclone", "lsf", f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # 過濾出照片檔案 (排除 manifest.json 和隱藏文件)
            files = result.stdout.strip().split('\n')
            photos = {
                f for f in files
                if f and not f.startswith('._') and f != '.DS_Store' and f != 'manifest.json'
                and any(f.lower().endswith(ext) for ext in PHOTO_EXTENSIONS)
            }
            return photos
        return set()
    except Exception as e:
        print(f"⚠️  無法取得 R2 照片列表: {e}")
        return set()


def sync_photo_to_r2(photo_name):
    """同步單張照片到 R2"""
    local_path = LOCAL_PHOTOS_DIR / photo_name
    remote_path = f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/{photo_name}"

    try:
        result = subprocess.run(
            ["rclone", "copy", str(local_path), f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  上傳失敗 {photo_name}: {e}")
        return False


def delete_photo_from_r2(photo_name):
    """從 R2 刪除照片"""
    remote_path = f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/{photo_name}"

    try:
        result = subprocess.run(
            ["rclone", "delete", remote_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  刪除失敗 {photo_name}: {e}")
        return False


def get_r2_photo_times():
    """取得 R2 上照片的修改時間"""
    try:
        result = subprocess.run(
            ["rclone", "lsl", f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            photo_times = {}
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                # rclone lsl format: "   size YYYY-MM-DD HH:MM:SS.NNNNNN filename"
                parts = line.split()
                if len(parts) >= 4:
                    filename = parts[-1]
                    if any(filename.lower().endswith(ext) for ext in PHOTO_EXTENSIONS):
                        # 使用日期時間字串作為排序依據
                        date_str = parts[1] + " " + parts[2]
                        photo_times[filename] = date_str
            return photo_times
        return {}
    except Exception as e:
        print(f"⚠️  無法取得 R2 照片時間: {e}")
        return {}


def update_r2_manifest(photos):
    """更新 R2 上的 manifest.json - 按上傳時間排序（最新在前），過濾隱藏文件"""
    # 過濾掉隱藏文件（._ 開頭）和 .DS_Store
    filtered_photos = {
        p for p in photos
        if not p.startswith('._') and p != '.DS_Store' and p != 'manifest.json'
    }
    
    # 取得照片的修改時間
    photo_times = get_r2_photo_times()

    # 按時間排序（最新的在前面），沒有時間資訊的放最後
    sorted_photos = sorted(
        list(filtered_photos),
        key=lambda p: photo_times.get(p, "0000-00-00 00:00:00"),
        reverse=True
    )
    
    # 再次驗證：確保沒有隱藏文件
    final_photos = [p for p in sorted_photos if not p.startswith('._')]
    
    manifest_content = json.dumps(final_photos, ensure_ascii=False, indent=2)

    # 寫入本地暫存檔
    local_manifest = LOCAL_PHOTOS_DIR / "manifest.json"
    with open(local_manifest, 'w', encoding='utf-8') as f:
        f.write(manifest_content)

    # 上傳到 R2
    try:
        result = subprocess.run(
            ["rclone", "copy", str(local_manifest), f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  更新 manifest 失敗: {e}")
        return False


def full_sync():
    """完整同步 (用於初始化或修復)"""
    print("🔄 執行完整同步...")

    try:
        result = subprocess.run(
            ["rclone", "sync", str(LOCAL_PHOTOS_DIR), f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/",
             "--include", "*.jpg", "--include", "*.jpeg", "--include", "*.png",
             "--include", "*.webp", "--include", "*.gif", "--include", "manifest.json",
             "-v"],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✅ 完整同步完成")
            return True
        else:
            print(f"⚠️  同步出現問題: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ 同步失敗: {e}")
        return False


def sync_static_files():
    """同步靜態資源 (event_settings.json, assets/)"""
    project_root = Path(__file__).parent
    
    # 1. Sync config/event_settings.json
    settings_file = project_root / "config" / "event_settings.json"
    if settings_file.exists():
        try:
            print(f"🔄 同步設定檔: {settings_file.name}")
            subprocess.run(
                ["rclone", "copy", str(settings_file), f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
                capture_output=True, timeout=30
            )
        except Exception as e:
            print(f"⚠️  同步設定檔失敗: {e}")

    # 2. Sync assets folder
    assets_dir = project_root / "assets"
    if assets_dir.exists():
        try:
            print(f"🔄 同步靜態資源目錄: {assets_dir.name}")
            subprocess.run(
                ["rclone", "copy", str(assets_dir), f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/assets/"],
                capture_output=True, timeout=60
            )
        except Exception as e:
            print(f"⚠️  同步靜態資源失敗: {e}")


def main():
    """主程式"""
    print("=" * 50)
    print("🚀 R2 自動同步腳本 - Live Event Photography")
    print("=" * 50)
    print(f"📂 監控資料夾: {LOCAL_PHOTOS_DIR}")
    print(f"☁️  R2 路徑: {RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/")
    print(f"⏱️  檢查間隔: {CHECK_INTERVAL} 秒")
    print("-" * 50)
    print("按 Ctrl+C 停止\n")

    # 初始同步靜態資源
    print("⚙️  同步靜態資源 (Settings & Assets)...")
    sync_static_files()

    # 初始化：取得目前狀態
    previous_local = get_local_photos()
    print(f"📸 本地照片: {len(previous_local)} 張")
    
    static_sync_counter = 0

    r2_photos = get_r2_photos()
    print(f"☁️  R2 照片: {len(r2_photos)} 張")

    # 檢查是否需要初始同步
    if previous_local != r2_photos:
        missing_in_r2 = previous_local - r2_photos
        extra_in_r2 = r2_photos - previous_local

        if extra_in_r2 and SAFE_MODE:
            print(f"\n📌 R2 有 {len(extra_in_r2)} 張照片不在本地")
            print("   🔒 安全模式：這些照片會保留在 R2")

        if missing_in_r2:
            print(f"\n⚠️  發現 {len(missing_in_r2)} 張本地照片尚未同步到 R2")
            print("   正在上傳...")
            for photo in missing_in_r2:
                if sync_photo_to_r2(photo):
                    print(f"   ✅ {photo}")
                else:
                    print(f"   ❌ {photo}")

            # 更新 manifest (安全模式從 R2 取得列表)
            if SAFE_MODE:
                actual_r2 = get_r2_photos()
                update_r2_manifest(actual_r2)
                print(f"   📋 Manifest 已更新 (R2: {len(actual_r2)} 張)")
            else:
                update_r2_manifest(previous_local)
                print("   📋 Manifest 已更新")

    print("\n🔍 開始監控變化...\n")

    loop_count = 0
    try:
        while True:
            # 每 10 次循環 (30秒) 同步一次靜態檔案
            if loop_count % 10 == 0 and loop_count > 0:
                sync_static_files()
            loop_count += 1

            current_local = get_local_photos()

            if current_local != previous_local:
                timestamp = datetime.now().strftime("%H:%M:%S")

                # 找出新增和刪除的照片
                added = current_local - previous_local
                removed = previous_local - current_local

                if added:
                    print(f"[{timestamp}] 📥 新增 {len(added)} 張照片")
                    for photo in added:
                        if sync_photo_to_r2(photo):
                            print(f"   ✅ 已上傳: {photo}")
                        else:
                            print(f"   ❌ 上傳失敗: {photo}")

                if removed:
                    if SAFE_MODE:
                        print(f"[{timestamp}] ⚠️  偵測到 {len(removed)} 張照片從本地移除")
                        print(f"   🔒 安全模式：R2 上的照片保持不變")
                        print(f"   （如需刪除，請設定 SAFE_MODE = False）")
                    else:
                        print(f"[{timestamp}] 🗑️  刪除 {len(removed)} 張照片")
                        for photo in removed:
                            if delete_photo_from_r2(photo):
                                print(f"   ✅ 已刪除: {photo}")
                            else:
                                print(f"   ❌ 刪除失敗: {photo}")

                # 更新 manifest
                if SAFE_MODE:
                    # 安全模式：從 R2 取得實際照片列表來更新 manifest
                    actual_r2_photos = get_r2_photos()
                    if update_r2_manifest(actual_r2_photos):
                        print(f"   📋 Manifest 已更新 (R2: {len(actual_r2_photos)} 張)")
                else:
                    if update_r2_manifest(current_local):
                        print(f"   📋 Manifest 已更新 ({len(current_local)} 張照片)")

                # 每 10 次迴圈 (約 30 秒) 同步一次靜態資源
                static_sync_counter += 1
                if static_sync_counter >= 10:
                    sync_static_files()
                    static_sync_counter = 0

                previous_local = current_local
                print()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n👋 同步腳本已停止")


if __name__ == "__main__":
    main()
