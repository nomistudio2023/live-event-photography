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

    def process_and_publish(self, filename: str, exposure: float = 0.0):
        """
        Reads from BUFFER, Applies Edits, Adds Watermark, Saves to WEB.
        """
        source_path = os.path.join(self.config["buffer_folder"], filename)
        dest_path = os.path.join(self.config["web_folder"], filename)
        
        # Change extension to .jpg for web if not already
        name, ext = os.path.splitext(filename)
        dest_path = os.path.join(self.config["web_folder"], name + ".jpg")

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {filename}")

        try:
            with Image.open(source_path) as img:
                # 1. Orientation Fix
                img = ImageOps.exif_transpose(img)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # 2. Exposure Compensation (New Feature!)
                # 1.0 is original. 1.2 is +20% brightness.
                # Mapping exposure (approx EV) to brightness multiplier:
                # 0EV = 1.0, +1EV ~= 2.0 brightness (roughly)
                # Let's use a simpler linear scale for now or 2^exposure
                brightness_factor = 2 ** exposure
                if exposure != 0.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness_factor)

                # 3. Resize
                max_size = self.config["max_size"]
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                # 4. Sharpen
                if self.config["processing"]["sharpen"]:
                    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

                # 5. Watermark
                img = self._apply_watermark(img)

                # 6. Save
                img.save(
                    dest_path, 
                    "JPEG", 
                    quality=self.config["jpeg_quality"], 
                    optimize=True, 
                    progressive=self.config["processing"]["progressive"]
                )
                
                logger.info(f"Published: {filename} (Exp: {exposure})")
                return True

        except Exception as e:
            logger.error(f"Processing failed: {e}")
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
                files.append({
                    "filename": f,
                    "timestamp": ts,
                    "time_str": datetime.fromtimestamp(ts).strftime('%H:%M:%S'),
                    "size_kb": round(stat.st_size / 1024, 1)
                })
        
        # Sort by timestamp (newest first)
        files.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"images": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/live")
async def get_live_images():
    """List images in Web Public folder"""
    try:
        files = [f for f in os.listdir(CONFIG["web_folder"]) 
                 if f.lower().endswith(('.jpg', '.jpeg')) and not f.startswith('.')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(CONFIG["web_folder"], x)), reverse=True)
        return {"images": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/publish")
async def publish_image(req: PublishRequest):
    """Action: Buffer -> Process -> Web"""
    try:
        processor.process_and_publish(req.filename, req.exposure)
        
        # Remove from buffer after successful publish? 
        # Usually yes, or move to a 'processed' folder. 
        # For now, let's KEEP it in buffer but maybe UI marks it as done.
        # actually, to keep buffer clean, let's move it to a 'processed' folder if desired.
        # But user might want to re-edit. Let's keep it for now.
        
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
            processor.process_and_publish(fname, req.exposure)
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
        target = os.path.join(CONFIG["web_folder"], req.filename)
        if os.path.exists(target):
            os.remove(target)
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
