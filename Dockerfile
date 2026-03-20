# ──────────────────────────────────────────────────
# LexiSight — Dockerfile
# Base: python:3.10-slim
# ──────────────────────────────────────────────────

FROM python:3.10-slim

# System dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /lexisight

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download TrOCR model at build time (optional but recommended)
# Comment this block out to skip pre-download and lazy-load at runtime
RUN python -c "\
from transformers import TrOCRProcessor, VisionEncoderDecoderModel; \
TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten'); \
VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten'); \
print('Model cached.')"

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
