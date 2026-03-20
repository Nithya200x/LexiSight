---
title: LexiSight
emoji: 📝
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# LexiSight

> Handwritten text extraction from images — built with TrOCR, FastAPI, and OpenCV.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)

---

## 🌐 Live Demo

Try it now — no installation needed:

**👉 https://nithya200x-lexisight.hf.space**

> Hosted on HuggingFace Spaces · Docker · Free tier

---

## What it does

Upload a photo of handwritten text. LexiSight detects the lines, preprocesses each one, runs it through Microsoft's TrOCR model, and returns structured output — extracted text, a short summary, detected headings, and optionally CER/WER accuracy scores if you provide a reference.

---

## Demo

> Run locally in demo mode (no model download needed):
>
> ```powershell
> $env:LEXISIGHT_DEMO="1"
> python -m uvicorn app.main:app --reload --port 8000
> ```
>
> Open **http://localhost:8000**

---

## Project Structure

```
LexiSight/
├── app/
│   ├── main.py               ← FastAPI app, routes, file validation
│   ├── pipeline.py           ← Orchestrates detect → preprocess → recognize
│   ├── detector.py           ← OpenCV line detection
│   ├── preprocessing.py      ← CLAHE enhancement + resize
│   ├── recognizer.py         ← TrOCR model inference
│   ├── schemas.py            ← Pydantic response model
│   ├── demo_mode.py          ← Mock pipeline for local dev
│   ├── utils/
│   │   └── metrics.py        ← CER + WER via Levenshtein distance
│   ├── services/
│   │   └── postprocess.py    ← Text cleaning, summary, heading detection
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── script.js
├── tests/
│   └── test_lexisight.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Nithya200x/LexiSight.git
cd LexiSight
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt --only-binary=numpy,Pillow,opencv-python-headless,torch
```

### 4. Run the server

```bash
# With real TrOCR model (downloads ~1.3GB on first run)
python -m uvicorn app.main:app --reload --port 8000

# Without model — instant demo mode
$env:LEXISIGHT_DEMO="1"    # Windows
export LEXISIGHT_DEMO=1    # macOS / Linux
python -m uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000**

---

## How It Works

```
Image uploaded
      │
      ▼
 detect_text_lines()     OpenCV adaptive threshold → dilation → contours
      │
      ▼
 preprocess_crop()       Grayscale → CLAHE → RGB → resize 384×384
      │
      ▼
 recognize_text()        TrOCR (microsoft/trocr-base-handwritten)
      │
      ▼
 clean_text()            Normalize whitespace, remove noise characters
      │
      ▼
 summarize()             First 1–2 sentences of extracted text
 detect_headings()       Uppercase or short title-style lines
      │
      ▼
 JSON response
```

---

## API

### `POST /ocr`

| Field          | Type   | Required | Description                           |
| -------------- | ------ | -------- | ------------------------------------- |
| `file`         | image  | ✅       | JPEG, PNG, WebP, BMP, TIFF — max 10MB |
| `ground_truth` | string | ❌       | Reference text for accuracy scoring   |

**Response**

```json
{
  "text": "Meeting Notes\nAttendees: Alice, Bob",
  "summary": "Meeting Notes. Attendees include Alice and Bob.",
  "headings": ["Meeting Notes"],
  "cer": 0.042,
  "wer": 0.083
}
```

`cer` and `wer` are `null` when no ground truth is provided.

### `GET /health`

```json
{ "status": "healthy", "service": "LexiSight OCR" }
```

---

## Accuracy Metrics

Computed from scratch using dynamic programming — no external metric libraries.

| Metric  | Formula                                              |
| ------- | ---------------------------------------------------- |
| **CER** | `levenshtein(ref_chars, hyp_chars) / len(ref_chars)` |
| **WER** | `levenshtein(ref_words, hyp_words) / len(ref_words)` |

Both return a value between `0.0` (perfect match) and `1.0` (no match).

---

## Docker

```bash
# Build
docker build -t lexisight .

# Run
docker run -p 8000:8000 lexisight

# Or with docker-compose (includes model cache volume)
docker-compose up
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

Tests cover the metrics, postprocessing, detector, preprocessor, and all API endpoints. The TrOCR model is mocked so no download is needed to run the test suite.

---

## Tips for Best Results

- Use a **clear, well-lit photo** — avoid shadows across the text
- **Black or dark pen on white paper** works best
- Higher resolution images produce better line detection
- Printed text also works, though the model is optimised for handwriting

---

## Tech Stack

| Layer       | Technology                               |
| ----------- | ---------------------------------------- |
| Model       | TrOCR — microsoft/trocr-base-handwritten |
| Backend     | FastAPI + Uvicorn                        |
| Image I/O   | Pillow                                   |
| CV Pipeline | OpenCV                                   |
| Inference   | PyTorch                                  |
| Validation  | Pydantic v2                              |
| Frontend    | Vanilla HTML / CSS / JS                  |
| Tests       | pytest                                   |

---

## Known Limitations

- Runs in demo mode on Hugging Face due to memory limits — full TrOCR inference requires ~2GB RAM
- Struggles with heavy cursive handwriting
- English only — other languages not supported
- Skewed or overlapping lines reduce detection accuracy
- No multi-page or PDF support
- Cold start on first request takes a few seconds

---

## Future Improvements

- [ ] Multi-language OCR support
- [ ] PDF and multi-page upload
- [ ] Auto deskew before line detection
- [ ] Per-line confidence scores
- [ ] Batch image processing
- [ ] OCR history with user accounts
- [ ] Fine-tune model on specific domains (medical, legal)

---

## License

MIT — free to use, modify, and distribute.
