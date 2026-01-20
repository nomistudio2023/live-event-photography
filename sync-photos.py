#!/usr/bin/env python3
"""
自動監視照片文件夾並同步到 GitHub
Auto-watch photos folder and sync to GitHub
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
REPO_ROOT = Path(__file__).parent
PHOTOS_DIR = REPO_ROOT / "photos_web"
MANIFEST_FILE = PHOTOS_DIR / "manifest.json"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def get_photo_list():
    """获取当前照片列表（已排序）"""
    if not PHOTOS_DIR.exists():
        return []

    photos = sorted([
        f.name for f in PHOTOS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in PHOTO_EXTENSIONS
    ])
    return photos

def load_manifest():
    """读取现有 manifest.json"""
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_manifest(photos):
    """保存 manifest.json"""
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)

def git_commit_push():
    """提交和推送到 GitHub"""
    try:
        os.chdir(REPO_ROOT)

        # 添加所有变更
        subprocess.run(["git", "add", "."], check=True, capture_output=True)

        # 检查是否有变更
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )

        if status.returncode != 0:  # 有变更
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Auto-sync photos - {timestamp}\n\nAuto-generated commit from sync script"

            subprocess.run(
                ["git", "commit", "-m", message],
                check=True,
                capture_output=True
            )

            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"✅ [{timestamp}] 已推送到 GitHub")
                return True
            else:
                print(f"❌ [{timestamp}] Git push 失败: {result.stderr}")
                return False
        else:
            print(f"⏭️  [{datetime.now().strftime('%H:%M:%S')}] 沒有文件變更")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 命令失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def main():
    """主循环"""
    print("🎬 Live Event Photo Sync - 自動同步腳本")
    print(f"📂 監視目錄: {PHOTOS_DIR}")
    print("⏱️  每 5 秒檢查一次文件變更\n")
    print("按 Ctrl+C 停止\n")

    previous_photos = set(load_manifest())

    try:
        while True:
            current_photos = set(get_photo_list())

            # 检查是否有变化
            if current_photos != previous_photos:
                print(f"\n📸 偵測到變更！")
                print(f"   舊照片数: {len(previous_photos)}")
                print(f"   新照片数: {len(current_photos)}")

                # 显示具体变化
                added = current_photos - previous_photos
                removed = previous_photos - current_photos

                if added:
                    print(f"   ✨ 新增: {', '.join(sorted(added))}")
                if removed:
                    print(f"   🗑️  删除: {', '.join(sorted(removed))}")

                # 更新 manifest.json
                new_manifest = sorted(list(current_photos))
                save_manifest(new_manifest)
                print(f"   📝 已更新 manifest.json")

                # 提交和推送
                if git_commit_push():
                    print(f"   🌐 Cloudflare Pages 將在 1-2 分鐘內自動部署\n")

                previous_photos = current_photos

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n👋 已停止監視")

if __name__ == "__main__":
    main()
