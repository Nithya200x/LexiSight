"""
recognizer.py — Text recognition using microsoft/trocr-base-handwritten.

Model is loaded lazily on first call and cached for subsequent requests.
Uses torch.no_grad() for efficient inference.
"""

import torch
from PIL import Image
from typing import Optional

# Lazy-loaded globals
_processor = None
_model = None
_device = None

MODEL_NAME = "microsoft/trocr-base-handwritten"


def _load_model():
    """Load TrOCR processor and model (called once)."""
    global _processor, _model, _device

    from transformers import TrOCRProcessor, VisionEncoderDecoderModel

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"[LexiSight] Loading TrOCR model on {_device}...")
    _processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
    _model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
    _model.to(_device)
    _model.eval()
    print("[LexiSight] Model loaded successfully.")


def recognize_text(image: Image.Image) -> str:
    """
    Run TrOCR inference on a preprocessed PIL Image.

    Args:
        image: PIL RGB Image (ideally 384×384)

    Returns:
        Recognized text string
    """
    global _processor, _model, _device

    # Lazy load on first call
    if _model is None:
        _load_model()

    # Prepare pixel values
    pixel_values = _processor(images=image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(_device)

    # Inference — no gradient computation needed
    with torch.no_grad():
        generated_ids = _model.generate(
            pixel_values,
            max_new_tokens=128
        )

    # Decode output tokens
    generated_text = _processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]

    return generated_text
