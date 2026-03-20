"""
pipeline.py — Orchestrates the full OCR pipeline:
  1. Detect text line regions
  2. Crop + preprocess each region
  3. Recognize text via TrOCR
  4. Combine into final string
"""

from PIL import Image
import numpy as np

from app.detector import detect_text_lines
from app.preprocessing import preprocess_crop
from app.recognizer import recognize_text


def run_ocr_pipeline(image: Image.Image) -> str:
    """
    Run full OCR pipeline on a PIL RGB image.
    Returns extracted text as a single string.
    """
    img_np = np.array(image)

    # Step 1: Detect line bounding boxes
    line_boxes = detect_text_lines(img_np)

    if not line_boxes:
        # Fallback: treat entire image as one region
        line_boxes = [(0, 0, img_np.shape[1], img_np.shape[0])]

    # Step 2–4: Crop, preprocess, recognize each line
    lines = []
    for (x, y, w, h) in line_boxes:
        # Crop with small padding
        pad = 4
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img_np.shape[1], x + w + pad)
        y2 = min(img_np.shape[0], y + h + pad)

        crop = img_np[y1:y2, x1:x2]

        # Skip extremely thin/empty crops
        if crop.shape[0] < 8 or crop.shape[1] < 8:
            continue

        # Preprocess crop → PIL image ready for model
        processed = preprocess_crop(crop)

        # Recognize text
        line_text = recognize_text(processed)
        if line_text.strip():
            lines.append(line_text.strip())

    return "\n".join(lines)
