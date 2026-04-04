# Project CV-06 - Object Detection System

Microservice CV system that detects 80 COCO object classes in images using YOLOv8 nano. Returns bounding boxes, confidence scores, class summary, and annotated image.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/detect                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/detect  →  calls cv-service          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  YOLOv8 nano inference (model auto-downloaded ~6MB)         │
│  Returns { detections[], class_summary, annotated_image }   │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

```
Image uploaded
    ↓
YOLOv8 nano inference (model auto-downloaded ~6MB)
    ↓
Filter by confidence threshold (0.4)
    ↓
Draw labeled bounding boxes on annotated image
    ↓
Return: detections[] + class_summary + annotated_image (base64)
```

---

## YOLO Model Options

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `yolov8n.pt` | 6MB | Fastest | Good |
| `yolov8s.pt` | 22MB | Fast | Better |
| `yolov8m.pt` | 52MB | Medium | Best local |

Change model in `cv-service/.env` → `MODEL_NAME=yolov8s.pt`

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI, Recharts |
| Backend | FastAPI, httpx |
| CV | Ultralytics YOLOv8, OpenCV, Pillow |
| Dataset | COCO (80 classes) — pretrained |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
# YOLOv8 model auto-downloaded on first request (~6MB)
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Object Detection API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `cv-service/.env`

```
MODEL_NAME=yolov8n.pt
CONFIDENCE_THRESHOLD=0.4
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-object-detection-system-cv-06/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/detector.py     ← YOLOv8 inference
│       └── main.py
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/detect
Body:     { "image": "<base64>", "confidence": 0.4 }
Response: { "detections": [{ "class": "person", "confidence": 92.1, "bounding_box": {...} }], "class_summary": { "person": 2 }, "annotated_image": "<base64>" }
```

---

## Dataset

Use any photo — try COCO validation images from Kaggle for testing all 80 classes.
