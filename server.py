import os
import json
import shutil
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

# Logger Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
CONFIG = {
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
            "image_path": "./assets/watermark.png",
            "position": "bottom-right",
            "opacity": 0.8,
            "scale_percentage": 20,
            "margin": 50
        }
    }
}

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
        if wm_conf['enabled'] and os.path.exists(wm_conf['image_path']):
            try:
                self.watermark_img = Image.open(wm_conf['image_path']).convert("RGBA")
                logger.info("Watermark loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load watermark: {e}")

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
                    # Rotate with expand to avoid cutting corners
                    img = img.rotate(straighten, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(0,0,0))

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

                    img = img.crop((left, top, right, bottom))

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
        if not self.watermark_img:
            return img
            
        wm_conf = self.config['processing']['watermark']
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
            
        # Position
        margin = wm_conf.get('margin', 30)
        # Default bottom-right
        x = img.width - wm.width - margin
        y = img.height - wm.height - margin
        
        # Safety bounds
        x = max(0, min(x, img.width - wm.width))
        y = max(0, min(y, img.height - wm.height))
        
        # Composite
        img_rgba = img.convert("RGBA")
        img_rgba.alpha_composite(wm, (x, y))
        return img_rgba.convert("RGB")

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

# Static Mounts
app.mount("/raw", StaticFiles(directory=CONFIG["buffer_folder"]), name="raw")
app.mount("/live", StaticFiles(directory=CONFIG["web_folder"]), name="live")
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

# Helpers
def update_manifest():
    """Generates manifest.json for the frontend"""
    try:
        folder = CONFIG["web_folder"]
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg'))]
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        
        manifest_path = os.path.join(folder, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
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
            if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('.'):
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

@app.post("/api/publish")
async def publish_image(req: PublishRequest):
    """Action: Buffer -> Process -> Web"""
    try:
        source_path = os.path.join(CONFIG["buffer_folder"], req.filename)
        name, ext = os.path.splitext(req.filename)
        dest_path = os.path.join(CONFIG["web_folder"], name + ".jpg") # Ensure .jpg for web

        processor.process_image(
            source_path, dest_path,
            exposure=req.exposure,
            rotation=req.rotation,
            straighten=req.straighten,
            scale=req.scale
        )

        # Update History
        update_history(req.filename, "publish")

        update_manifest()
        return {"status": "success", "filename": req.filename}
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

@app.post("/api/unpublish")
async def unpublish_image(req: UnpublishRequest):
    """Action: Web -> Remove (Hide from public)"""
    try:
        # We don't delete the Source file, just the Web file.
        name, ext = os.path.splitext(req.filename)
        target_filename = name + ".jpg" # Ensure .jpg for web
        target = os.path.join(CONFIG["web_folder"], target_filename)
        if os.path.exists(target):
            os.remove(target)
            update_history(req.filename, "unpublish") # Update history for unpublish
            update_manifest()
            return {"status": "unpublished", "filename": req.filename}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Command Center Starting...")
    print("👉 Admin Dashboard: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
