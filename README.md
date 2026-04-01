# Project 06 - Object Detection System (CV)

Detect 80 COCO object classes in images using YOLOv8 nano. Returns bounding boxes, confidence scores, class summary, and annotated image.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/YOLOv8
```

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

## What's Different from Projects 01-05

| | P01 | P02 | P03 | P04 | P05 | P06 |
|---|---|---|---|---|---|---|
| Model | SVM | DNN SSD | Tesseract | Filters | Cosine | YOLOv8 |
| Classes | 10 | 1 (face) | N/A | N/A | N/A | 80 COCO |
| Speed | Slow | Fast | Slow | Fast | Fast | Real-time |
| New concept | sklearn | OpenCV DNN | OCR | Filters | Embeddings | YOLO |

## YOLO Model Options

| Model | Size | Speed | Accuracy |
|---|---|---|---|
| `yolov8n.pt` | 6MB | Fastest | Good |
| `yolov8s.pt` | 22MB | Fast | Better |
| `yolov8m.pt` | 52MB | Medium | Best local |

## Local Run

```bash
# Terminal 1 - CV Service (YOLOv8 model auto-downloaded on first request)
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- CV Service docs: http://localhost:8001/docs
- Backend docs:   http://localhost:8000/docs
- UI:             http://localhost:3000

## Docker

```bash
docker-compose up --build
```

## Dataset
Use any photo — try COCO validation images from Kaggle for testing all 80 classes.
