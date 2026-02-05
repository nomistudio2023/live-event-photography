#!/usr/bin/env python3
"""
R2 照片管理工具 - Live Event Photography
用於列出、刪除 R2 上的照片

使用方式：
    python3 r2_manage.py list              # 列出所有照片
    python3 r2_manage.py delete 照片名.jpg  # 刪除指定照片
    python3 r2_manage.py delete-multi      # 互動式多選刪除
    python3 r2_manage.py refresh           # 重新整理 manifest（按時間排序）
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# ============ 配置（與 sync_to_r2.py 相同）============
RCLONE_REMOTE = "r2livegallery"
BUCKET_NAME = "nomilivegallery"
R2_PATH_PREFIX = "2026-01-20"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
LOCAL_PHOTOS_DIR = Path(__file__).parent / "photos_web"
# =====================================================


def get_r2_photos_with_time():
    """取得 R2 照片列表及時間"""
    try:
        result = subprocess.run(
            ["rclone", "lsl", f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            photos = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    size = int(parts[0])
                    date_str = parts[1]
                    time_str = parts[2].split('.')[0]  # 移除毫秒
                    filename = parts[-1]
                    if any(filename.lower().endswith(ext) for ext in PHOTO_EXTENSIONS):
                        photos.append({
                            'name': filename,
                            'size': size,
                            'date': date_str,
                            'time': time_str,
                            'datetime': f"{date_str} {time_str}"
                        })
            # 按時間排序（最新在前）
            photos.sort(key=lambda x: x['datetime'], reverse=True)
            return photos
        return []
    except Exception as e:
        print(f"❌ 無法取得 R2 照片列表: {e}")
        return []


def delete_photo(photo_name):
    """刪除指定照片"""
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
        print(f"❌ 刪除失敗: {e}")
        return False


def update_manifest():
    """更新 R2 上的 manifest"""
    photos = get_r2_photos_with_time()
    photo_names = [p['name'] for p in photos]

    manifest_content = json.dumps(photo_names, ensure_ascii=False, indent=2)

    # 寫入本地暫存檔
    local_manifest = LOCAL_PHOTOS_DIR / "manifest.json"
    with open(local_manifest, 'w', encoding='utf-8') as f:
        f.write(manifest_content)

    # 上傳到 R2
    try:
        result = subprocess.run(
            ["rclone", "copy", str(local_manifest),
             f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 更新 manifest 失敗: {e}")
        return False


def cmd_list():
    """列出所有照片"""
    print("📋 R2 照片列表（按上傳時間排序，最新在前）\n")
    photos = get_r2_photos_with_time()

    if not photos:
        print("（無照片）")
        return

    print(f"{'#':<4} {'檔名':<30} {'大小':>10} {'上傳時間':<20}")
    print("-" * 70)

    for i, photo in enumerate(photos, 1):
        size_kb = photo['size'] / 1024
        print(f"{i:<4} {photo['name']:<30} {size_kb:>8.1f}KB {photo['datetime']:<20}")

    print("-" * 70)
    print(f"共 {len(photos)} 張照片")


def cmd_delete(photo_name):
    """刪除指定照片"""
    photos = get_r2_photos_with_time()
    photo_names = [p['name'] for p in photos]

    if photo_name not in photo_names:
        print(f"❌ 找不到照片: {photo_name}")
        print("   使用 'python3 r2_manage.py list' 查看所有照片")
        return

    confirm = input(f"確定要刪除 {photo_name}？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    print(f"🗑️  正在刪除 {photo_name}...")
    if delete_photo(photo_name):
        print("✅ 已刪除")
        print("📋 正在更新 manifest...")
        if update_manifest():
            print("✅ Manifest 已更新")
        else:
            print("⚠️  Manifest 更新失敗，請手動執行 refresh")
    else:
        print("❌ 刪除失敗")


def cmd_delete_multi():
    """互動式多選刪除"""
    photos = get_r2_photos_with_time()

    if not photos:
        print("（無照片可刪除）")
        return

    print("📋 選擇要刪除的照片（輸入編號，用空格或逗號分隔）\n")
    print(f"{'#':<4} {'檔名':<30} {'上傳時間':<20}")
    print("-" * 60)

    for i, photo in enumerate(photos, 1):
        print(f"{i:<4} {photo['name']:<30} {photo['datetime']:<20}")

    print("-" * 60)
    print("\n輸入要刪除的編號（例如: 1 3 5 或 1,3,5）")
    print("輸入 'q' 取消")

    selection = input("\n選擇: ").strip()

    if selection.lower() == 'q':
        print("已取消")
        return

    # 解析選擇
    try:
        # 支援空格或逗號分隔
        nums = [int(x.strip()) for x in selection.replace(',', ' ').split()]
        selected_photos = []
        for num in nums:
            if 1 <= num <= len(photos):
                selected_photos.append(photos[num - 1]['name'])
            else:
                print(f"⚠️  無效編號: {num}")
    except ValueError:
        print("❌ 輸入格式錯誤")
        return

    if not selected_photos:
        print("未選擇任何照片")
        return

    print(f"\n將刪除以下 {len(selected_photos)} 張照片:")
    for name in selected_photos:
        print(f"  - {name}")

    confirm = input(f"\n確定刪除？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 執行刪除
    success = 0
    for name in selected_photos:
        print(f"🗑️  刪除 {name}...", end=" ")
        if delete_photo(name):
            print("✅")
            success += 1
        else:
            print("❌")

    print(f"\n刪除完成: {success}/{len(selected_photos)}")

    # 更新 manifest
    print("📋 正在更新 manifest...")
    if update_manifest():
        print("✅ Manifest 已更新")
    else:
        print("⚠️  Manifest 更新失敗")


def cmd_refresh():
    """重新整理 manifest"""
    print("🔄 正在重新整理 manifest（按上傳時間排序）...")

    photos = get_r2_photos_with_time()
    print(f"   找到 {len(photos)} 張照片")

    if update_manifest():
        print("✅ Manifest 已更新")
        print("\n前 5 張照片（最新）:")
        for photo in photos[:5]:
            print(f"   {photo['name']} ({photo['datetime']})")
    else:
        print("❌ 更新失敗")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == 'list':
        cmd_list()
    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print("用法: python3 r2_manage.py delete 照片名.jpg")
            return
        cmd_delete(sys.argv[2])
    elif cmd == 'delete-multi':
        cmd_delete_multi()
    elif cmd == 'refresh':
        cmd_refresh()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
