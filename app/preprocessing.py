"""
preprocessing.py — Preprocesses a cropped line image for TrOCR input.

Steps:
  1. Convert to grayscale
  2. Apply CLAHE (contrast enhancement)
  3. Convert back to RGB (TrOCR expects RGB)
  4. Resize to 384×384
  5. Return as PIL Image
"""

import cv2
import numpy as np
from PIL import Image


TARGET_SIZE = (384, 384)


def preprocess_crop(crop: np.ndarray) -> Image.Image:
    """
    Preprocess a numpy image crop for the TrOCR model.

    Args:
        crop: numpy array (H, W, 3) in RGB format

    Returns:
        PIL Image (RGB, 384×384)
    """
    # Step 1: Grayscale
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop.copy()

    # Step 2: CLAHE — Contrast Limited Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Step 3: Back to RGB (TrOCR processor expects 3-channel)
    rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

    # Step 4: Resize to target size
    resized = cv2.resize(rgb, TARGET_SIZE, interpolation=cv2.INTER_CUBIC)

    # Step 5: Convert to PIL
    pil_image = Image.fromarray(resized.astype(np.uint8))

    return pil_image
