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

            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True
            )

            if commit_result.returncode == 0:
                print(f"   commit OK")

                # 尝试推送
                result = subprocess.run(
                    ["git", "push", "origin", "main"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print(f"✅ [{timestamp}] Pushed to GitHub - Cloudflare Pages will deploy in 1-2 minutes")
                    return True
                else:
                    print(f"⚠️  [{timestamp}] Local commit OK, but push to GitHub failed")
                    print(f"   Error: {result.stderr[:200]}")
                    print(f"   Please run: git push origin main")
                    return False
            else:
                print(f"Commit failed: {commit_result.stderr}")
                return False
        else:
            return False

    except subprocess.TimeoutExpired:
        print(f"Push timeout - possible network issue")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """主循环"""
    print("🎬 Live Event Photo Sync - Auto-sync script")
    print(f"📂 Monitoring: {PHOTOS_DIR}")
    print("Check for changes every 5 seconds\n")
    print("Press Ctrl+C to stop\n")

    previous_photos = set(load_manifest())

    try:
        while True:
            current_photos = set(get_photo_list())

            # 检查是否有变化
            if current_photos != previous_photos:
                print(f"\n📸 Changes detected!")
                print(f"   Old photos: {len(previous_photos)}")
                print(f"   New photos: {len(current_photos)}")

                # 显示具体变化
                added = current_photos - previous_photos
                removed = previous_photos - current_photos

                if added:
                    print(f"   Add: {', '.join(sorted(list(added)[:3]))}", end='')
                    if len(added) > 3:
                        print(f" ... and {len(added) - 3} more")
                    else:
                        print()
                if removed:
                    print(f"   Delete: {', '.join(sorted(list(removed)[:3]))}", end='')
                    if len(removed) > 3:
                        print(f" ... and {len(removed) - 3} more")
                    else:
                        print()

                # 更新 manifest.json
                new_manifest = sorted(list(current_photos))
                save_manifest(new_manifest)
                print(f"   Updated manifest.json\n")

                # 提交和推送
                git_commit_push()

                previous_photos = current_photos

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n👋 Stopped")

if __name__ == "__main__":
    main()
