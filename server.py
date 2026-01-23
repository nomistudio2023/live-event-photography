import os
import json
import shutil
import logging
import time
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont

# Logger Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
DEFAULT_CONFIG = {
    "buffer_folder": "./photos_buffer",   # Camera Ingest (Raw-ish)
    "web_folder": "./photos_web",         # Live Public
    "trash_folder": "./photos_trash",     # Rejected
    "archive_folder": "./photos_archive", # Parked/Saved for later
    "assets_folder": "./assets",
    "history_file": "history.json",
    "max_size": 1600,
    "jpeg_quality": 85,
    "processing": {
        "sharpen": True,
        "progressive": True,
        "watermark": {
            "enabled": True,
            "type": "image",  # "image" or "text"
            "image_path": "./assets/watermark.png",
            "text": "",  # Text watermark content
            "text_font_size": 24,
            "text_color": [255, 255, 255, 200],
            "position": "bottom-right",
            "opacity": 0.8,
            "scale_percentage": 20,
            "margin": 50
        }
    }
}

def load_config_file():
    """Load config from JSON file if exists, otherwise use default CONFIG"""
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                # Merge with default CONFIG
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(file_config)
                # Ensure nested dicts are merged properly
                if "processing" in file_config:
                    if merged_config.get("processing"):
                        merged_config["processing"].update(file_config["processing"])
                    else:
                        merged_config["processing"] = file_config["processing"]
                if "watermark" in file_config.get("processing", {}):
                    if merged_config["processing"].get("watermark"):
                        merged_config["processing"]["watermark"].update(file_config["processing"]["watermark"])
                    else:
                        merged_config["processing"]["watermark"] = file_config["processing"]["watermark"]
                return merged_config
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
    return DEFAULT_CONFIG.copy()

# Load config from file (will use DEFAULT_CONFIG if file doesn't exist)
CONFIG = load_config_file()

# Ensure directories exist
for folder in [CONFIG["buffer_folder"], CONFIG["web_folder"], CONFIG["trash_folder"], CONFIG["archive_folder"]]:
    os.makedirs(folder, exist_ok=True)

# --- History Management ---
def load_history():
    if os.path.exists(CONFIG["history_file"]):
        try:
            with open(CONFIG["history_file"], "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history file: {e}")
            return {}
    return {}

def save_history(history):
    try:
        with open(CONFIG["history_file"], "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save history file: {e}")

def update_history(filename, action):
    """
    action: 'publish' or 'unpublish'
    """
    history = load_history()
    # Ensure filename is consistent (e.g., always .jpg for web)
    name, ext = os.path.splitext(filename)
    processed_filename = name + ".jpg"

    if processed_filename not in history:
        history[processed_filename] = {"published": 0, "unpublished": 0}
    
    if action == "publish":
        history[processed_filename]["published"] += 1
    elif action == "unpublish":
        history[processed_filename]["unpublished"] += 1
        
    save_history(history)

def get_file_history(filename):
    history = load_history()
    name, ext = os.path.splitext(filename)
    processed_filename = name + ".jpg"
    return history.get(processed_filename, {"published": 0, "unpublished": 0})

# --- Image Processor Logic (Integrated) ---
class ImageProcessor:
    def __init__(self, config):
        self.config = config
        self.watermark_img = None
        self.load_assets()

    def load_assets(self):
        wm_conf = self.config['processing']['watermark']
        if wm_conf['enabled']:
            if wm_conf.get('type', 'image') == 'image' and os.path.exists(wm_conf.get('image_path', '')):
                try:
                    self.watermark_img = Image.open(wm_conf['image_path']).convert("RGBA")
                    logger.info("Watermark image loaded successfully.")
                except Exception as e:
                    logger.error(f"Failed to load watermark image: {e}")
            # Text watermark doesn't need pre-loading

    def process_image(self, source_path: str, dest_path: str, exposure: float = 0.0,
                       rotation: int = 0, straighten: float = 0.0, scale: float = 1.0):
        """
        Applies edits (exposure, rotation, straighten, scale) and watermark to an image and saves it.

        Args:
            rotation: 90° increments (0, 90, 180, 270)
            straighten: Fine angle adjustment (-5 to +5 degrees), will crop to remove black edges
            scale: Zoom level (1.0 = 100%, >1.0 = zoom in with center crop)
        """
        import math

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        try:
            with Image.open(source_path) as img:
                # 1. Orientation Fix (EXIF)
                img = ImageOps.exif_transpose(img)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # 2. Rotation (90° increments)
                if rotation == 90:
                    img = img.transpose(Image.Transpose.ROTATE_270)  # PIL rotates counter-clockwise
                elif rotation == 180:
                    img = img.transpose(Image.Transpose.ROTATE_180)
                elif rotation == 270:
                    img = img.transpose(Image.Transpose.ROTATE_90)

                # Store original dimensions after 90° rotation
                orig_w, orig_h = img.width, img.height

                # 3. Straighten (fine angle adjustment with proper crop)
                if straighten != 0:
                    # PIL rotate() is counter-clockwise, but CSS rotate() is clockwise
                    # Negate the angle to match preview direction
                    pil_angle = -straighten
                    logger.info(f"   🔄 Applying straighten: {straighten}° (PIL angle: {pil_angle}°)")
                    logger.info(f"      Before rotate: {img.width}x{img.height}")
                    img = img.rotate(pil_angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(0,0,0))
                    logger.info(f"      After rotate: {img.width}x{img.height}")

                    # Calculate the largest inscribed rectangle after rotation
                    # to crop out the black edges
                    angle_rad = abs(math.radians(straighten))
                    cos_a = math.cos(angle_rad)
                    sin_a = math.sin(angle_rad)

                    # For small angles, calculate crop dimensions
                    # The inscribed rectangle formula for rotated image
                    if orig_w > orig_h:
                        # Landscape
                        new_w = int(orig_w * cos_a - orig_h * sin_a)
                        new_h = int(orig_h * cos_a - orig_w * sin_a)
                    else:
                        # Portrait
                        new_w = int(orig_w * cos_a - orig_h * sin_a)
                        new_h = int(orig_h * cos_a - orig_w * sin_a)

                    # Ensure positive dimensions (use simpler formula for small angles)
                    # For angles < 10°, approximate: crop factor ≈ 1 - tan(angle) * aspect_adjustment
                    crop_factor = cos_a - sin_a * min(orig_w/orig_h, orig_h/orig_w)
                    crop_factor = max(0.8, min(1.0, crop_factor))  # Clamp to reasonable range

                    new_w = int(orig_w * crop_factor)
                    new_h = int(orig_h * crop_factor)

                    # Center crop
                    left = (img.width - new_w) // 2
                    top = (img.height - new_h) // 2
                    right = left + new_w
                    bottom = top + new_h

                    logger.info(f"      Crop: ({left},{top}) to ({right},{bottom}) -> {new_w}x{new_h}")
                    img = img.crop((left, top, right, bottom))
                    logger.info(f"      After crop: {img.width}x{img.height}")

                # 4. Scale (zoom) - crop from center when zooming in
                if scale != 1.0 and scale > 0.5:
                    if scale > 1.0:
                        # Zoom in: crop a smaller region from center
                        crop_w = int(img.width / scale)
                        crop_h = int(img.height / scale)
                        left = (img.width - crop_w) // 2
                        top = (img.height - crop_h) // 2
                        right = left + crop_w
                        bottom = top + crop_h
                        img = img.crop((left, top, right, bottom))
                    else:
                        # Zoom out (scale < 1.0): just resize smaller, will be handled by thumbnail later
                        pass

                # 5. Exposure Compensation
                brightness_factor = 2 ** exposure
                if exposure != 0.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness_factor)

                # 6. Resize to max size
                max_size = self.config["max_size"]
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                # 7. Sharpen
                if self.config["processing"]["sharpen"]:
                    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

                # 8. Watermark
                img = self._apply_watermark(img)

                # 9. Save
                img.save(
                    dest_path,
                    "JPEG",
                    quality=self.config["jpeg_quality"],
                    optimize=True,
                    progressive=self.config["processing"]["progressive"]
                )

                logger.info(f"Processed: {os.path.basename(source_path)} -> {dest_path} "
                           f"(Exp:{exposure}, Rot:{rotation}, Str:{straighten}, Scale:{scale})")
                return True

        except Exception as e:
            logger.error(f"Processing failed for {source_path}: {e}")
            raise e

    def _apply_watermark(self, img):
        wm_conf = self.config['processing']['watermark']
        if not wm_conf.get('enabled', False):
            return img
        
        watermark_type = wm_conf.get('type', 'image')
        margin = wm_conf.get('margin', 50)
        position = wm_conf.get('position', 'bottom-right')
        
        img_rgba = img.convert("RGBA")
        
        if watermark_type == 'text':
            # Text watermark
            text = wm_conf.get('text', '')
            if not text:
                return img_rgba.convert("RGB")
            
            # Create text image
            font_size = wm_conf.get('text_font_size', 24)
            text_color = tuple(wm_conf.get('text_color', (255, 255, 255, 200)))
            
            try:
                # Try to load a font that supports Chinese characters
                # macOS system fonts that support Chinese
                font_paths = [
                    "/System/Library/Fonts/PingFang.ttc",  # PingFang (supports Chinese)
                    "/System/Library/Fonts/STHeiti Light.ttc",  # STHeiti (supports Chinese)
                    "/System/Library/Fonts/STHeiti Medium.ttc",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf",
                ]
                font = None
                for font_path in font_paths:
                    try:
                        if font_path.endswith('.ttc'):
                            # TTC files may contain multiple fonts, try index 0
                            font = ImageFont.truetype(font_path, font_size, index=0)
                            break
                        else:
                            font = ImageFont.truetype(font_path, font_size)
                            break
                    except:
                        continue
                if font is None:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Create a temporary image to measure text size
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Create text image with background
            text_img = Image.new('RGBA', (text_width + 20, text_height + 10), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((10, 5), text, font=font, fill=text_color)
            
            # Calculate position
            x, y = self._calculate_watermark_position(img.width, img.height, text_width + 20, text_height + 10, position, margin)
            
            # Composite text watermark
            img_rgba.alpha_composite(text_img, (x, y))
            
        elif watermark_type == 'image' and self.watermark_img:
            # Image watermark
            wm = self.watermark_img.copy()
            
            # Scale
            scale = wm_conf.get('scale_percentage', 20) / 100
            target_wm_width = int(min(img.size) * scale)
            wm_ratio = target_wm_width / wm.width
            new_wm_size = (int(wm.width * wm_ratio), int(wm.height * wm_ratio))
            wm = wm.resize(new_wm_size, Image.Resampling.LANCZOS)
            
            # Opacity
            opacity = wm_conf.get('opacity', 0.8)
            if opacity < 1.0:
                alpha = wm.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                wm.putalpha(alpha)
            
            # Calculate position
            x, y = self._calculate_watermark_position(img.width, img.height, wm.width, wm.height, position, margin)
            
            # Composite image watermark
            img_rgba.alpha_composite(wm, (x, y))
        
        return img_rgba.convert("RGB")
    
    def _calculate_watermark_position(self, img_width, img_height, wm_width, wm_height, position, margin):
        """Calculate watermark position based on position string"""
        if position == "bottom-right":
            x = img_width - wm_width - margin
            y = img_height - wm_height - margin
        elif position == "bottom-left":
            x = margin
            y = img_height - wm_height - margin
        elif position == "top-right":
            x = img_width - wm_width - margin
            y = margin
        elif position == "top-left":
            x = margin
            y = margin
        elif position == "center":
            x = (img_width - wm_width) // 2
            y = (img_height - wm_height) // 2
        elif position == "top-center":
            x = (img_width - wm_width) // 2
            y = margin
        elif position == "bottom-center":
            x = (img_width - wm_width) // 2
            y = img_height - wm_height - margin
        else:
            # Default to bottom-right
            x = img_width - wm_width - margin
            y = img_height - wm_height - margin
        
        # Safety bounds
        x = max(0, min(x, img_width - wm_width))
        y = max(0, min(y, img_height - wm_height))
        
        return x, y

# Initialize Processor
processor = ImageProcessor(CONFIG)

# --- FastAPI App ---
app = FastAPI(title="Live Photo Command Center")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom endpoint for live images with no-cache headers
@app.get("/live/{filename:path}")
async def serve_live_image(filename: str):
    """Serve live images with no-cache headers to ensure updates are visible"""
    from fastapi.responses import Response
    import time

    file_path = os.path.join(CONFIG["web_folder"], filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Read file content directly to bypass FileResponse caching
    with open(file_path, "rb") as f:
        content = f.read()

    # Use current timestamp as ETag to force browser to fetch fresh content
    etag = f'"{int(time.time() * 1000)}"'

    return Response(
        content=content,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "ETag": etag
        }
    )

# Static Mounts
app.mount("/raw", StaticFiles(directory=CONFIG["buffer_folder"]), name="raw")
# Mount photos_web to match the path expected by index.html
app.mount("/photos_web", StaticFiles(directory=CONFIG["web_folder"]), name="photos_web")
app.mount("/assets", StaticFiles(directory=CONFIG["assets_folder"]), name="assets")

templates = Jinja2Templates(directory="templates")

# Models
class PublishRequest(BaseModel):
    filename: str
    exposure: float = 0.0
    rotation: int = 0        # 0, 90, 180, 270
    straighten: float = 0.0  # -5 to +5 degrees
    scale: float = 1.0       # 0.5 to 1.5

class RejectRequest(BaseModel):
    filename: str

class BatchPublishRequest(BaseModel):
    filenames: List[str]
    exposure: float = 0.0

class ArchiveRequest(BaseModel):
    filename: str

class UnpublishRequest(BaseModel):
    filename: str

class EventSettingsRequest(BaseModel):
    event_title: str
    event_subtitle: str
    hero_image_url: Optional[str] = None
    title_font_family: Optional[str] = None
    title_font_size: Optional[int] = None
    subtitle_font_family: Optional[str] = None
    subtitle_font_size: Optional[int] = None

class WatermarkSettingsRequest(BaseModel):
    enabled: bool
    type: str = "image"  # "image" or "text"
    text: Optional[str] = None
    text_font_size: int = 24
    text_color: List[int] = [255, 255, 255, 200]
    position: str = "bottom-right"
    opacity: float = 0.8
    scale_percentage: float = 20
    margin: int = 50

class FolderSettingsRequest(BaseModel):
    buffer_folder: str
    web_folder: str
    trash_folder: str
    archive_folder: str

# Helpers
def update_manifest():
    """Generates manifest.json for the frontend"""
    try:
        folder = CONFIG["web_folder"]
        if not os.path.exists(folder):
            logger.warning(f"Web folder does not exist: {folder}")
            return
        
        # Only include files that actually exist, are valid image files, and are readable
        files = []
        for f in os.listdir(folder):
            # Skip macOS hidden files (._ prefix), .DS_Store, and manifest.json
            if f.startswith('._') or f == '.DS_Store' or f == 'manifest.json':
                continue
            
            if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'manifest.json':
                file_path = os.path.join(folder, f)
                # Ensure it's a file, not a directory, and is readable
                if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                    # Verify file size > 0 (not empty/corrupted)
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > 0:
                            # Try to verify it's a valid image by checking if PIL can open it
                            try:
                                with Image.open(file_path) as img:
                                    img.verify()  # Verify it's a valid image
                                files.append(f)
                            except Exception as img_error:
                                logger.warning(f"Skipping invalid image file: {f} ({img_error})")
                                continue
                        else:
                            logger.warning(f"Skipping empty file: {f}")
                    except Exception as e:
                        logger.warning(f"Error checking file {f}: {e}")
                        continue
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        
        manifest_path = os.path.join(folder, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
        logger.info(f"Manifest updated: {len(files)} photos")
    except Exception as e:
        logger.error(f"Manifest update failed: {e}")

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/gallery", response_class=HTMLResponse)
async def gallery():
    """Serve the public facing live gallery"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading gallery: {e}"

@app.get("/api/buffer")
async def get_buffer_images():
    """List images in Camera Buffer with metadata"""
    try:
        folder = CONFIG["buffer_folder"]
        files = []
        for f in os.listdir(folder):
            # Skip macOS hidden files (._ prefix) and .DS_Store
            if f.startswith('._') or f == '.DS_Store' or f.startswith('.'):
                continue
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(folder, f)
                stat = os.stat(path)
                # Use modification time as a proxy for capture time if simple
                ts = stat.st_mtime
                
                hist = get_file_history(f) # Get history for buffer files
                
                files.append({
                    "filename": f,
                    "timestamp": ts,
                    "time_str": datetime.fromtimestamp(ts).strftime('%H:%M:%S'),
                    "size_kb": round(stat.st_size / 1024, 1),
                    "published_count": hist["published"],
                    "unpublished_count": hist["unpublished"]
                })
        
        # Sort by timestamp (newest first)
        files.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"images": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/status")
async def get_system_status():
    """Get system status including sync script status"""
    import subprocess

    # Check if sync_to_r2.py is running
    sync_running = False
    try:
        result = subprocess.run(
            ["pgrep", "-f", "sync_to_r2.py"],
            capture_output=True, text=True, timeout=2
        )
        sync_running = result.returncode == 0
    except:
        pass

    return {
        "server": True,  # If this endpoint responds, server is running
        "sync": sync_running,
        "web_folder": CONFIG["web_folder"],
        "buffer_folder": CONFIG["buffer_folder"]
    }


@app.get("/api/live")
async def get_live_images():
    """List images in Web Public folder with metadata"""
    try:
        folder = CONFIG["web_folder"]
        files = []
        for f in os.listdir(folder):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('.'):
                path = os.path.join(folder, f)
                stat = os.stat(path)
                ts = stat.st_mtime
                
                # Get History
                hist = get_file_history(f)
                
                files.append({
                    "filename": f,
                    "timestamp": ts,
                    "time_str": datetime.fromtimestamp(ts).strftime('%H:%M:%S'),
                    "size_kb": round(stat.st_size / 1024, 1),
                    "published_count": hist["published"],
                    "unpublished_count": hist["unpublished"]
                })
        
        # Sort by timestamp (newest first)
        files.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"images": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

def get_next_publish_filename(base_name: str, web_folder: str) -> str:
    """
    Generate sequential filename for multiple publishes of the same source.
    First publish: 15D_7109.jpg
    Second publish: 15D_7109_002.jpg
    Third publish: 15D_7109_003.jpg
    """
    import re

    # Check existing files with same base name
    existing_files = []
    for f in os.listdir(web_folder):
        # Skip macOS hidden files (._ prefix) and .DS_Store
        if f.startswith('._') or f == '.DS_Store':
            continue
        if f.lower().endswith(('.jpg', '.jpeg')):
            # Match base_name or base_name_NNN pattern
            if f == f"{base_name}.jpg" or f.startswith(f"{base_name}_"):
                existing_files.append(f)

    if not existing_files:
        # First publish - use original name
        return f"{base_name}.jpg"

    # Find highest sequence number
    max_seq = 1  # Original file counts as 001
    for f in existing_files:
        if f == f"{base_name}.jpg":
            continue  # Original file
        # Extract sequence number from pattern like base_name_002.jpg
        match = re.search(rf'{re.escape(base_name)}_(\d{{3}})\.jpg', f)
        if match:
            seq = int(match.group(1))
            max_seq = max(max_seq, seq)

    # Generate next sequence
    next_seq = max_seq + 1
    return f"{base_name}_{next_seq:03d}.jpg"


@app.post("/api/publish")
async def publish_image(req: PublishRequest):
    """Action: Buffer -> Process -> Web"""
    try:
        source_path = os.path.join(CONFIG["buffer_folder"], req.filename)
        name, ext = os.path.splitext(req.filename)

        # Generate sequential filename if same source published multiple times
        dest_filename = get_next_publish_filename(name, CONFIG["web_folder"])
        dest_path = os.path.join(CONFIG["web_folder"], dest_filename)

        # Debug log to verify parameters
        logger.info(f"📥 Publish request: {req.filename}")
        logger.info(f"   └─ Exposure={req.exposure}, Rotation={req.rotation}, Straighten={req.straighten}, Scale={req.scale}")
        logger.info(f"   └─ Output: {dest_filename}")

        processor.process_image(
            source_path, dest_path,
            exposure=req.exposure,
            rotation=req.rotation,
            straighten=req.straighten,
            scale=req.scale
        )

        # Verify file was written and is valid
        if not os.path.exists(dest_path):
            logger.error(f"   ❌ File NOT found after save: {dest_path}")
            raise HTTPException(status_code=500, detail=f"Failed to save processed image: {dest_path}")
        
        file_size = os.path.getsize(dest_path)
        if file_size == 0:
            logger.error(f"   ❌ File is empty: {dest_path}")
            os.remove(dest_path)  # Remove empty file
            raise HTTPException(status_code=500, detail="Processed image file is empty")
        
        # Verify it's a valid image
        try:
            with Image.open(dest_path) as img:
                img.verify()
        except Exception as img_error:
            logger.error(f"   ❌ Invalid image file: {img_error}")
            os.remove(dest_path)  # Remove invalid file
            raise HTTPException(status_code=500, detail=f"Invalid image file: {img_error}")
        
        logger.info(f"   ✅ File saved: {dest_filename} ({file_size/1024:.1f}KB)")

        # Update History (track source filename)
        update_history(req.filename, "publish")

        update_manifest()
        # Return both source and published filename
        return {"status": "success", "filename": req.filename, "published_as": dest_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch_publish")
async def batch_publish_images(req: BatchPublishRequest):
    """Publish multiple images at once"""
    success_count = 0
    errors = []
    
    for fname in req.filenames:
        try:
            source_path = os.path.join(CONFIG["buffer_folder"], fname)
            name, ext = os.path.splitext(fname)
            dest_path = os.path.join(CONFIG["web_folder"], name + ".jpg") # Ensure .jpg for web

            processor.process_image(source_path, dest_path, req.exposure)
            update_history(fname, "publish")
            success_count += 1
        except Exception as e:
            errors.append(f"{fname}: {str(e)}")
            
    update_manifest()
    return {"status": "completed", "success": success_count, "errors": errors}

@app.post("/api/archive")
async def archive_image(req: ArchiveRequest):
    """Action: Buffer -> Archive (Park)"""
    try:
        src = os.path.join(CONFIG["buffer_folder"], req.filename)
        dst = os.path.join(CONFIG["archive_folder"], req.filename)
        if os.path.exists(src):
            shutil.move(src, dst)
            return {"status": "archived", "filename": req.filename}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reject")
async def reject_image(req: RejectRequest):
    """Action: Buffer -> Trash"""
    try:
        src = os.path.join(CONFIG["buffer_folder"], req.filename)
        dst = os.path.join(CONFIG["trash_folder"], req.filename)
        if os.path.exists(src):
            shutil.move(src, dst)
            return {"status": "rejected", "filename": req.filename}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def sync_delete_to_r2(filename: str):
    """Delete a file from R2 and update R2 manifest"""
    import subprocess
    import json

    # R2 config (matching sync_to_r2.py)
    RCLONE_REMOTE = "r2livegallery"
    BUCKET_NAME = "nomilivegallery"
    R2_PATH_PREFIX = "2026-01-20"

    remote_path = f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/{filename}"

    # 1. Delete file from R2
    try:
        result = subprocess.run(
            ["rclone", "delete", remote_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            logger.info(f"   ☁️ R2 deleted: {filename}")
        else:
            logger.warning(f"   ⚠️ R2 delete failed: {result.stderr[:100]}")
            return  # Don't update manifest if delete failed
    except Exception as e:
        logger.warning(f"   ⚠️ R2 delete error: {e}")
        return

    # 2. Get current R2 photo list (to rebuild manifest accurately)
    try:
        # List all photos in R2 (excluding manifest.json)
        result = subprocess.run(
            ["rclone", "lsf", f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            r2_files = result.stdout.strip().split('\n')
            r2_photos = [
                f for f in r2_files
                if f and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))
            ]
            
            # Get photo times for sorting (similar to sync_to_r2.py)
            photo_times = {}
            if r2_photos:
                result = subprocess.run(
                    ["rclone", "lsl", f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) >= 4:
                            date_str = parts[1]
                            time_str = parts[2].split('.')[0]
                            photo_name = parts[-1]
                            if photo_name in r2_photos:
                                photo_times[photo_name] = f"{date_str} {time_str}"
            
            # Sort by time (newest first)
            sorted_photos = sorted(
                r2_photos,
                key=lambda p: photo_times.get(p, "0000-00-00 00:00:00"),
                reverse=True
            )
            
            # Create manifest content
            manifest_content = json.dumps(sorted_photos, ensure_ascii=False, indent=2)
            
            # Write to local manifest first
            manifest_path = os.path.join(CONFIG["web_folder"], "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest_content)
            
            # Upload to R2
            result = subprocess.run(
                ["rclone", "copy", manifest_path,
                 f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                logger.info(f"   ☁️ R2 manifest updated ({len(sorted_photos)} photos)")
            else:
                logger.warning(f"   ⚠️ R2 manifest update failed: {result.stderr[:100]}")
        else:
            # Fallback: just copy local manifest
            manifest_path = os.path.join(CONFIG["web_folder"], "manifest.json")
            if os.path.exists(manifest_path):
                result = subprocess.run(
                    ["rclone", "copy", manifest_path,
                     f"{RCLONE_REMOTE}:{BUCKET_NAME}/{R2_PATH_PREFIX}/"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    logger.info(f"   ☁️ R2 manifest updated (fallback)")
    except Exception as e:
        logger.warning(f"   ⚠️ R2 manifest sync error: {e}")


@app.post("/api/unpublish")
async def unpublish_image(req: UnpublishRequest):
    """Action: Web -> Remove (Hide from public + R2)"""
    try:
        name, ext = os.path.splitext(req.filename)
        target_filename = name + ".jpg"
        target = os.path.join(CONFIG["web_folder"], target_filename)
        if os.path.exists(target):
            # 1. Delete local file
            os.remove(target)
            logger.info(f"🗑 Unpublish: {target_filename}")

            # 2. Update history
            update_history(req.filename, "unpublish")

            # 3. Update local manifest
            update_manifest()

            # 4. Sync deletion to R2 (async-safe via thread)
            import threading
            threading.Thread(
                target=sync_delete_to_r2,
                args=(target_filename,),
                daemon=True
            ).start()

            return {"status": "unpublished", "filename": req.filename}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Event Settings Management ---
EVENT_SETTINGS_FILE = "event_settings.json"

def load_event_settings():
    """Load event settings from JSON file"""
    if os.path.exists(EVENT_SETTINGS_FILE):
        try:
            with open(EVENT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load event settings: {e}")
    return {
        "event_title": "LIVE EVENT 2026",
        "event_subtitle": "即時活動花絮・精彩瞬間",
        "hero_image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80",
        "hero_image_uploaded": None,
        "title_font_family": "Arial, sans-serif",
        "title_font_size": 56,
        "subtitle_font_family": "Arial, sans-serif",
        "subtitle_font_size": 20
    }

def save_event_settings(settings):
    """Save event settings to JSON file"""
    try:
        with open(EVENT_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save event settings: {e}")
        return False

@app.get("/api/event-settings")
async def get_event_settings():
    """Get current event settings"""
    return load_event_settings()

@app.post("/api/event-settings")
async def update_event_settings(req: EventSettingsRequest):
    """Update event settings"""
    current = load_event_settings()
    settings = {
        "event_title": req.event_title,
        "event_subtitle": req.event_subtitle,
        "hero_image_url": req.hero_image_url or current.get("hero_image_url", ""),
        "hero_image_uploaded": current.get("hero_image_uploaded"),
        "title_font_family": req.title_font_family or current.get("title_font_family", "Arial, sans-serif"),
        "title_font_size": req.title_font_size or current.get("title_font_size", 56),
        "subtitle_font_family": req.subtitle_font_family or current.get("subtitle_font_family", "Arial, sans-serif"),
        "subtitle_font_size": req.subtitle_font_size or current.get("subtitle_font_size", 20)
    }
    if save_event_settings(settings):
        return {"status": "success", "settings": settings}
    else:
        raise HTTPException(status_code=500, detail="Failed to save event settings")

@app.post("/api/upload-hero-image")
async def upload_hero_image(file: UploadFile = File(...)):
    """Upload hero background image"""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        filename_lower = file.filename.lower()
        if not filename_lower.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG, WEBP files are allowed")
        
        # Save to assets folder
        assets_folder = CONFIG.get("assets_folder", "./assets")
        os.makedirs(assets_folder, exist_ok=True)
        
        ext = filename_lower.split('.')[-1]
        filename = f"hero_bg_{int(time.time())}.{ext}"
        file_path = os.path.join(assets_folder, filename)
        
        # Read and save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update event settings
        settings = load_event_settings()
        settings["hero_image_uploaded"] = f"/assets/{filename}"
        save_event_settings(settings)
        
        return {"status": "success", "url": f"/assets/{filename}", "filename": filename}
    except Exception as e:
        logger.error(f"Failed to upload hero image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-watermark")
async def upload_watermark(file: UploadFile = File(...)):
    """Upload watermark image"""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        filename_lower = file.filename.lower()
        if not filename_lower.endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG files are allowed")
        
        # Save to assets folder (replace existing watermark.png)
        assets_folder = CONFIG.get("assets_folder", "./assets")
        os.makedirs(assets_folder, exist_ok=True)
        
        file_path = os.path.join(assets_folder, "watermark.png")
        
        # Read and save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Reload processor to load new watermark
        processor.load_assets()
        
        return {"status": "success", "message": "Watermark uploaded successfully"}
    except Exception as e:
        logger.error(f"Failed to upload watermark: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/watermark-settings")
async def get_watermark_settings():
    """Get current watermark settings"""
    return CONFIG["processing"]["watermark"]

@app.post("/api/watermark-settings")
async def update_watermark_settings(req: WatermarkSettingsRequest):
    """Update watermark settings"""
    CONFIG["processing"]["watermark"].update({
        "enabled": req.enabled,
        "type": req.type,
        "text": req.text or "",
        "text_font_size": req.text_font_size,
        "text_color": req.text_color,
        "position": req.position,
        "opacity": req.opacity,
        "scale_percentage": req.scale_percentage,
        "margin": req.margin
    })
    
    # Reload processor with new settings
    processor.load_assets()
    
    # Save to config file
    try:
        config_file = "config.json"
        with open(config_file, "r", encoding="utf-8") as f:
            file_config = json.load(f)
    except:
        file_config = {}
    
    if "processing" not in file_config:
        file_config["processing"] = {}
    file_config["processing"]["watermark"] = CONFIG["processing"]["watermark"]
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(file_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save config file: {e}")
    
    return {"status": "success", "watermark": CONFIG["processing"]["watermark"]}

@app.get("/api/folder-settings")
async def get_folder_settings():
    """Get current folder settings"""
    return {
        "buffer_folder": CONFIG["buffer_folder"],
        "web_folder": CONFIG["web_folder"],
        "trash_folder": CONFIG["trash_folder"],
        "archive_folder": CONFIG["archive_folder"]
    }

@app.post("/api/folder-settings")
async def update_folder_settings(req: FolderSettingsRequest):
    """Update folder settings"""
    # Validate folders exist or create them
    folders = {
        "buffer_folder": req.buffer_folder,
        "web_folder": req.web_folder,
        "trash_folder": req.trash_folder,
        "archive_folder": req.archive_folder
    }
    
    for folder_name, folder_path in folders.items():
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"Created folder: {folder_path}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to create folder {folder_path}: {e}")
    
    # Update CONFIG
    CONFIG.update(folders)
    
    # Save to config file
    try:
        config_file = "config.json"
        with open(config_file, "r", encoding="utf-8") as f:
            file_config = json.load(f)
    except:
        file_config = {}
    
    file_config.update(folders)
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(file_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save config file: {e}")
    
    return {"status": "success", "folders": folders}

# --- Cloudflare Pages Deployment ---
GITHUB_REPO_PATH = "/Users/nomisas/Documents/GitHub/live-event-photography"

@app.get("/api/deployment-status")
async def get_deployment_status():
    """Check deployment status and Git repository status"""
    import subprocess
    
    result = {
        "repo_exists": False,
        "has_changes": False,
        "last_commit": None,
        "remote_status": "unknown"
    }
    
    if not os.path.exists(GITHUB_REPO_PATH):
        return result
    
    result["repo_exists"] = True
    
    try:
        # Check if there are uncommitted changes
        check_changes = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        result["has_changes"] = bool(check_changes.stdout.strip())
        
        # Get last commit info
        last_commit = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "log", "-1", "--format=%H|%s|%cd", "--date=iso"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if last_commit.returncode == 0 and last_commit.stdout:
            parts = last_commit.stdout.strip().split('|')
            if len(parts) >= 3:
                result["last_commit"] = {
                    "hash": parts[0][:7],
                    "message": parts[1],
                    "date": parts[2]
                }
        
        # Check remote status
        remote_status = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "status", "-sb"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if remote_status.returncode == 0:
            if "ahead" in remote_status.stdout:
                result["remote_status"] = "ahead"
            elif "behind" in remote_status.stdout:
                result["remote_status"] = "behind"
            else:
                result["remote_status"] = "synced"
    
    except Exception as e:
        logger.error(f"Failed to check deployment status: {e}")
        result["error"] = str(e)
    
    return result

@app.post("/api/deploy-to-cloudflare")
async def deploy_to_cloudflare():
    """Deploy event_settings.json to GitHub and trigger Cloudflare Pages deployment"""
    import subprocess
    
    if not os.path.exists(GITHUB_REPO_PATH):
        raise HTTPException(
            status_code=404, 
            detail=f"GitHub repository not found at {GITHUB_REPO_PATH}\n\n請確認 GitHub 倉庫路徑是否正確，或修改 server.py 中的 GITHUB_REPO_PATH 變數。"
        )
    
    if not os.path.exists(EVENT_SETTINGS_FILE):
        raise HTTPException(status_code=404, detail="event_settings.json not found")
    
    try:
        # Copy event_settings.json to GitHub repo
        dest_path = os.path.join(GITHUB_REPO_PATH, "event_settings.json")
        shutil.copy2(EVENT_SETTINGS_FILE, dest_path)
        logger.info(f"Copied event_settings.json to {dest_path}")
        
        # Check if git repo is initialized
        git_dir = os.path.join(GITHUB_REPO_PATH, ".git")
        if not os.path.exists(git_dir):
            raise HTTPException(
                status_code=400, 
                detail=f"Git repository not initialized at {GITHUB_REPO_PATH}\n\n請先執行：\ncd {GITHUB_REPO_PATH}\ngit init\ngit remote add origin <your-repo-url>"
            )
        
        # Check git status first
        status_result = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Stage the file
        add_result = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "add", "event_settings.json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if add_result.returncode != 0:
            error_msg = add_result.stderr or add_result.stdout
            logger.error(f"Git add failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Git add 失敗: {error_msg}")
        
        # Commit
        commit_message = f"Update event settings - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_result = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            timeout=10
        )
        if commit_result.returncode != 0:
            # Check if there are actually changes to commit
            output_lower = (commit_result.stdout + commit_result.stderr).lower()
            if "nothing to commit" in output_lower or "no changes" in output_lower:
                return {
                    "status": "info",
                    "message": "沒有變更需要提交（設定可能已經是最新的）"
                }
            error_msg = commit_result.stderr or commit_result.stdout
            logger.error(f"Git commit failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Git commit 失敗: {error_msg}")
        
        # Check if remote is configured
        remote_result = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "remote", "-v"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if remote_result.returncode != 0 or not remote_result.stdout.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Git remote 未設定\n\n請執行：\ngit -C {GITHUB_REPO_PATH} remote add origin <your-repo-url>"
            )
        
        # Push to remote
        push_result = subprocess.run(
            ["git", "-C", GITHUB_REPO_PATH, "push"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if push_result.returncode != 0:
            error_output = push_result.stderr or push_result.stdout
            error_lower = error_output.lower()
            
            # Check for authentication errors
            if any(keyword in error_lower for keyword in ["permission denied", "authentication", "unauthorized", "access denied"]):
                raise HTTPException(
                    status_code=401,
                    detail="Git 認證失敗\n\n請確保已設定：\n1. SSH key（推薦）\n2. 或 Personal Access Token\n\n詳細設定請參考 DEPLOYMENT_GUIDE.md"
                )
            elif "could not read" in error_lower or "repository not found" in error_lower:
                raise HTTPException(
                    status_code=404,
                    detail=f"無法找到遠端倉庫\n\n請確認 remote URL 是否正確：\ngit -C {GITHUB_REPO_PATH} remote -v"
                )
            else:
                logger.error(f"Git push failed: {error_output}")
                raise HTTPException(status_code=500, detail=f"Git push 失敗: {error_output}")
        
        logger.info("Successfully pushed to GitHub, Cloudflare Pages should deploy automatically")
        return {
            "status": "success",
            "message": "✅ 已成功推送到 GitHub，Cloudflare Pages 正在自動部署中（通常需要 1-3 分鐘）",
            "commit": commit_message
        }
    
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Git 操作超時，請檢查網路連接")
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"部署失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Command Center Starting...")
    print("👉 Admin Dashboard: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
