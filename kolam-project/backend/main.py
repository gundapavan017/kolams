"""
Kolam Analysis API  —  FastAPI Backend
=======================================
Endpoints:
  GET  /                    health check
  POST /api/analyze         upload a Kolam image → rules + recreation + variations
  POST /api/generate        generate a Kolam from chosen parameters
  GET  /api/gallery         returns all 6 pre-generated Kolam types
"""

import io
import numpy as np
import cv2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from modules.analyzer import KolamAnalyzer
from modules.generator import KolamGenerator, DRAWERS

app = FastAPI(title="Kolam Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer  = KolamAnalyzer()
generator = KolamGenerator()


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"status": "ok", "message": "Kolam API is running"}


# ── Analyze ───────────────────────────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_kolam(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    # Resize large images to speed up analysis
    h, w = img.shape[:2]
    if max(h, w) > 1024:
        scale = 1024 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    rules       = analyzer.analyze(img)
    recreated   = generator.recreate(rules)
    variations  = generator.generate_variations(rules, count=3)

    return JSONResponse({
        "rules":      rules,
        "recreated":  recreated,
        "variations": variations,
    })


# ── Generate ──────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    pattern: str = "Flower Kolam"
    color:   str = "#FF6B35"
    size:    int = 3


@app.post("/api/generate")
def generate_kolam(req: GenerateRequest):
    valid_patterns = list(DRAWERS.keys())
    if req.pattern not in valid_patterns:
        raise HTTPException(status_code=400,
                            detail=f"Pattern must be one of: {valid_patterns}")
    size = max(1, min(req.size, 6))
    image = generator.generate_from_params(req.pattern, req.color, size)
    return JSONResponse({"image": image, "pattern": req.pattern})


# ── Gallery ───────────────────────────────────────────────────────────────────

@app.get("/api/gallery")
def gallery():
    images = generator.generate_all()
    return JSONResponse({"kolams": images})


# ── Pattern list ──────────────────────────────────────────────────────────────

@app.get("/api/patterns")
def patterns():
    return JSONResponse({"patterns": list(DRAWERS.keys())})


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
