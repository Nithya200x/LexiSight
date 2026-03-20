"""
detector.py — Detects text line bounding boxes from a numpy image
using OpenCV morphological operations + contour analysis.
"""

import cv2
import numpy as np
from typing import List, Tuple


def detect_text_lines(img_np: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detect text line regions in a BGR/RGB numpy image.

    Returns a list of (x, y, w, h) bounding boxes sorted top-to-bottom.
    """
    # Convert to grayscale
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np.copy()

    # Adaptive threshold to binarize
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=15,
        C=8
    )

    # Morphological dilation to connect characters into lines
    # Wide horizontal kernel merges letters/words on the same line
    h, w = binary.shape
    kernel_w = max(20, w // 30)
    kernel_h = max(3, h // 80)
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (kernel_w, kernel_h)
    )
    dilated = cv2.dilate(binary, kernel, iterations=2)

    # Find contours of dilated regions
    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return []

    boxes = []
    img_area = h * w
    for cnt in contours:
        x, y, bw, bh = cv2.boundingRect(cnt)
        area = bw * bh

        # Filter noise: skip tiny boxes or boxes covering almost entire image
        if area < 0.0005 * img_area:
            continue
        if bw < 10 or bh < 6:
            continue

        boxes.append((x, y, bw, bh))

    # Sort top-to-bottom, then left-to-right
    boxes.sort(key=lambda b: (b[1], b[0]))

    return boxes
