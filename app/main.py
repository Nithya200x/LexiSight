from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import os
from PIL import Image

from app.schemas import OCRResponse
from app.pipeline import run_ocr_pipeline
from app.utils.metrics import compute_cer, compute_wer
from app.services.postprocess import clean_text, summarize, detect_headings

app = FastAPI(
    title="LexiSight OCR API",
    description="Premium Handwritten OCR System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "LexiSight API is running. Use POST /ocr to extract text."}


@app.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(
    file: UploadFile = File(...),
    ground_truth: str = Form(default=None)
):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed: JPEG, PNG, WebP, BMP, TIFF."
        )

    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(contents) // 1024}KB). Maximum allowed: 10MB."
        )

    # Load image
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode image: {str(e)}")

    # Run OCR pipeline
    try:
        raw_text = run_ocr_pipeline(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR pipeline failed: {str(e)}")

    # Post-process
    text = clean_text(raw_text)
    summary = summarize(text)
    headings = detect_headings(text)

    # Metrics
    cer = None
    wer = None
    if ground_truth and ground_truth.strip():
        cer = compute_cer(ground_truth.strip(), text)
        wer = compute_wer(ground_truth.strip(), text)

    return OCRResponse(
        text=text,
        summary=summary,
        headings=headings,
        cer=round(cer, 4) if cer is not None else None,
        wer=round(wer, 4) if wer is not None else None
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LexiSight OCR"}
