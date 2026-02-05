#!/usr/bin/env python3
"""
清理 macOS 隱藏文件工具
移除 photos_web 資料夾中的 ._ 開頭文件和 .DS_Store
"""

import os
import json
from pathlib import Path

def load_config():
    """Load config from config.json"""
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  無法讀取 config.json: {e}")
    
    # Default paths
    return {
        "web_folder": "./photos_web",
        "buffer_folder": "./photos_buffer",
        "trash_folder": "./photos_trash",
        "archive_folder": "./photos_archive"
    }

def clean_hidden_files(folder_path):
    """Remove hidden files from folder"""
    if not os.path.exists(folder_path):
        print(f"⚠️  資料夾不存在: {folder_path}")
        return 0
    
    removed_count = 0
    removed_files = []
    
    for f in os.listdir(folder_path):
        # Check for macOS hidden files
        if f.startswith('._') or f == '.DS_Store':
            file_path = os.path.join(folder_path, f)
            try:
                os.remove(file_path)
                removed_count += 1
                removed_files.append(f)
                print(f"  ✅ 已刪除: {f}")
            except Exception as e:
                print(f"  ❌ 刪除失敗 {f}: {e}")
    
    return removed_count, removed_files

def clean_manifest(folder_path):
    """Clean manifest.json to remove hidden file entries"""
    manifest_path = os.path.join(folder_path, "manifest.json")
    
    if not os.path.exists(manifest_path):
        print(f"⚠️  manifest.json 不存在: {manifest_path}")
        return False
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        # Filter out hidden files
        cleaned = [f for f in manifest if not f.startswith('._') and f != '.DS_Store' and f != 'manifest.json']
        hidden_in_manifest = [f for f in manifest if f.startswith('._')]
        
        if hidden_in_manifest:
            print(f"\n📋 清理 manifest.json:")
            print(f"  原始: {len(manifest)} 個項目")
            print(f"  清理後: {len(cleaned)} 個項目")
            print(f"  移除的隱藏文件: {hidden_in_manifest}")
            
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ manifest.json 已清理")
            return True
        else:
            print(f"  ℹ️  manifest.json 已經是乾淨的")
            return False
    
    except Exception as e:
        print(f"  ❌ 清理 manifest 失敗: {e}")
        return False

def main():
    print("=" * 60)
    print("🧹 清理 macOS 隱藏文件工具")
    print("=" * 60)
    print()
    
    config = load_config()
    
    folders_to_clean = [
        ("Web 資料夾", config.get("web_folder", "./photos_web")),
        ("Buffer 資料夾", config.get("buffer_folder", "./photos_buffer")),
        ("Trash 資料夾", config.get("trash_folder", "./photos_trash")),
        ("Archive 資料夾", config.get("archive_folder", "./photos_archive"))
    ]
    
    total_removed = 0
    
    for folder_name, folder_path in folders_to_clean:
        print(f"📂 檢查 {folder_name}: {folder_path}")
        
        if not os.path.exists(folder_path):
            print(f"  ⚠️  資料夾不存在，跳過\n")
            continue
        
        # Clean hidden files
        removed_count, removed_files = clean_hidden_files(folder_path)
        total_removed += removed_count
        
        if removed_count > 0:
            print(f"  ✅ 已刪除 {removed_count} 個隱藏文件\n")
        else:
            print(f"  ℹ️  沒有發現隱藏文件\n")
        
        # Clean manifest if it's web folder
        if folder_name == "Web 資料夾":
            clean_manifest(folder_path)
    
    print("=" * 60)
    print(f"✅ 清理完成！總共刪除 {total_removed} 個隱藏文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
