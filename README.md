# LexiSight — Premium Handwritten OCR System

> AI-powered handwritten text extraction with a modern, production-ready interface.

---

## ✨ Features

| Feature | Details |
|---|---|
| **OCR Engine** | `microsoft/trocr-base-handwritten` via HuggingFace Transformers |
| **Line Detection** | OpenCV morphological dilation + contour analysis |
| **Preprocessing** | Grayscale → CLAHE → Resize 384×384 |
| **Post-processing** | Text cleaning, extractive summary, heading detection |
| **Accuracy Metrics** | CER & WER via pure-Python Levenshtein (no external libs) |
| **Backend** | FastAPI with file validation, error handling |
| **Frontend** | Dark glassmorphism UI, drag-and-drop, live metrics |
| **Deployment** | Docker-ready |

---

## 🗂️ Project Structure

```
lexisight/
├── app/
│   ├── main.py               ← FastAPI app + endpoints
│   ├── pipeline.py           ← OCR orchestration
│   ├── detector.py           ← OpenCV line detection
│   ├── preprocessing.py      ← CLAHE image preprocessing
│   ├── recognizer.py         ← TrOCR inference
│   ├── schemas.py            ← Pydantic models
│   ├── utils/
│   │   └── metrics.py        ← CER / WER (Levenshtein DP)
│   ├── services/
│   │   └── postprocess.py    ← clean_text, summarize, detect_headings
│   └── static/
│       ├── index.html        ← Frontend
│       ├── styles.css        ← Premium dark UI
│       └── script.js         ← Drag-drop, OCR call, results render
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🚀 Quick Start

### Local (Python 3.10+)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

### Docker

```bash
# Build image (downloads TrOCR model during build)
docker build -t lexisight .

# Run container
docker run -p 8000:8000 lexisight
```

---

## 🌐 API

### `POST /ocr`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | `UploadFile` | ✅ | Image (JPEG/PNG/WebP/BMP/TIFF, max 10MB) |
| `ground_truth` | `string` | ❌ | Reference text for CER/WER evaluation |

**Response:**
```json
{
  "text": "Hello World\nThis is a handwritten note.",
  "summary": "Hello World. This is a handwritten note.",
  "headings": ["HELLO WORLD"],
  "cer": 0.0423,
  "wer": 0.0833
}
```

### `GET /health`
```json
{ "status": "healthy", "service": "LexiSight OCR" }
```

---

## 📐 Metrics

Both metrics are computed without external libraries using **Levenshtein distance** via dynamic programming:

- **CER** = `edit_distance(ref_chars, hyp_chars) / len(ref_chars)`
- **WER** = `edit_distance(ref_words, hyp_words) / len(ref_words)`

Values range from `0.0` (perfect) to `1.0` (completely wrong).

---

## 🖼️ How the OCR Pipeline Works

```
Input Image
    ↓
detect_text_lines()    ← OpenCV: adaptive threshold → dilation → contours
    ↓
For each line bounding box:
    crop + pad
    ↓
preprocess_crop()      ← grayscale → CLAHE → RGB → resize 384×384
    ↓
recognize_text()       ← TrOCR (microsoft/trocr-base-handwritten)
    ↓
Combine lines → raw text
    ↓
clean_text()           ← normalize, remove noise
    ↓
summarize()            ← first 1–2 sentences
detect_headings()      ← uppercase / short title lines
    ↓
OCRResponse
```

---

## 🛠️ Tech Stack

- **Python 3.10**
- **FastAPI** — async REST backend
- **HuggingFace Transformers** — TrOCR model
- **PyTorch** — inference with `torch.no_grad()`
- **OpenCV** — image processing & text detection
- **Pillow** — image I/O
- **Pydantic v2** — request/response validation

---

## 📸 Best Results

- Use **clear, well-lit photos** of handwritten text
- **Black pen on white paper** works best
- Higher resolution = better line detection
- Provide ground truth to measure accuracy

---

*Built for college projects, hackathons, and portfolio showcases.*
