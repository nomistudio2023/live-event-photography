#!/usr/bin/env python3
"""
修復 R2 上的 manifest.json - 清理隱藏文件
"""

import json
import subprocess
import os

# 從 config.json 讀取設定
def load_config():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# R2 設定
RCLONE_REMOTE = "r2livegallery"
BUCKET_NAME = "nomilivegallery"
R2_PATH_PREFIX = "2026-01-20"

def get_r2_manifest():
    """從 R2 下載 manifest.json"""
    try:
        temp_dir = "./temp_r2_download"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 下載 manifest.json
        result = subprocess.run(
            ["rclone", "copy", 
             f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/manifest.json",
             temp_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        temp_manifest = os.path.join(temp_dir, "manifest.json")
        if result.returncode == 0 and os.path.exists(temp_manifest):
            with open(temp_manifest, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            os.remove(temp_manifest)
            os.rmdir(temp_dir)
            return manifest
        else:
            if os.path.exists(temp_dir):
                if os.path.exists(temp_manifest):
                    os.remove(temp_manifest)
                os.rmdir(temp_dir)
            print("⚠️  無法從 R2 下載 manifest.json（可能不存在）")
            return None
    except Exception as e:
        print(f"⚠️  下載 manifest 失敗: {e}")
        return None

def clean_and_upload_manifest():
    """清理並上傳 manifest.json 到 R2"""
    print("=" * 60)
    print("🔧 修復 R2 manifest.json")
    print("=" * 60)
    print()
    
    # 1. 從本地讀取（應該已經清理過）
    config = load_config()
    web_folder = config.get("web_folder", "./photos_web")
    local_manifest_path = os.path.join(web_folder, "manifest.json")
    
    if not os.path.exists(local_manifest_path):
        print(f"❌ 本地 manifest.json 不存在: {local_manifest_path}")
        return False
    
    # 讀取本地 manifest
    with open(local_manifest_path, "r", encoding="utf-8") as f:
        local_manifest = json.load(f)
    
    print(f"📋 本地 manifest: {len(local_manifest)} 個照片")
    
    # 清理本地 manifest（確保沒有隱藏文件）
    cleaned = [f for f in local_manifest if not f.startswith('._') and f != '.DS_Store' and f != 'manifest.json']
    hidden_in_local = [f for f in local_manifest if f.startswith('._')]
    
    if hidden_in_local:
        print(f"⚠️  本地 manifest 包含隱藏文件: {hidden_in_local}")
        print(f"   清理後: {len(cleaned)} 個有效照片")
    
    # 2. 從 R2 下載當前 manifest
    r2_manifest = get_r2_manifest()
    if r2_manifest:
        print(f"📋 R2 manifest: {len(r2_manifest)} 個項目")
        hidden_in_r2 = [f for f in r2_manifest if f.startswith('._')]
        if hidden_in_r2:
            print(f"⚠️  R2 manifest 包含隱藏文件: {hidden_in_r2}")
    
    # 3. 使用清理後的本地 manifest
    final_manifest = cleaned
    print(f"\n✅ 將上傳 {len(final_manifest)} 個有效照片到 R2")
    print(f"   照片列表: {final_manifest}")
    
    # 4. 使用本地已清理的 manifest（直接上傳）
    # 確保本地 manifest 是乾淨的
    with open(local_manifest_path, "w", encoding="utf-8") as f:
        json.dump(final_manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 本地 manifest 已更新為清理版本")
    
    # 5. 上傳到 R2（使用 rclone copy，會覆蓋現有文件）
    try:
        result = subprocess.run(
            ["rclone", "copy", local_manifest_path,
             f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"\n✅ R2 manifest.json 已更新！")
            print(f"   包含 {len(final_manifest)} 個有效照片")
            return True
        else:
            print(f"\n❌ 上傳失敗: {result.stderr}")
            return False
    except Exception as e:
        print(f"\n❌ 上傳失敗: {e}")
        return False

if __name__ == "__main__":
    success = clean_and_upload_manifest()
    if success:
        print("\n" + "=" * 60)
        print("✅ 修復完成！請刷新活動頁面查看效果")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 修復失敗，請檢查錯誤訊息")
        print("=" * 60)
