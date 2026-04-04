# GCP Deployment Guide — Project CV-06 Object Detection System

---

## GCP Services for Object Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Vision API — Object Localization** | Detect objects with bounding boxes and confidence scores              | Replace your YOLOv8 pipeline                       |
| **Vertex AI AutoML Vision**          | Train a custom object detector on your labelled images — no code needed      | When you need domain-specific object categories    |
| **Vertex AI Gemini Vision**          | Gemini Pro Vision for custom object detection via prompt                     | When you need flexible object detection            |

> **Cloud Vision API Object Localization** is the direct replacement for your YOLOv8 pipeline. It returns bounding boxes + confidence for common objects — no model download needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images and annotated detection results                     |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track detection latency, object counts, request volume                    |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Cloud Vision API Object Localization│
│ CV Service :8001  │    │ or Vertex AI AutoML Vision         │
│ YOLOv8 nano       │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create objdetect-cv-project --name="Object Detection"
gcloud config set project objdetect-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com vision.googleapis.com \
  aiplatform.googleapis.com storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create objdetect-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/objdetect-cv-project/objdetect-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Cloud Vision API Object Localization

```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()

def detect_objects(image_bytes: bytes) -> dict:
    image = vision.Image(content=image_bytes)
    response = client.object_localization(image=image)
    detections, class_summary = [], {}
    for obj in response.localized_object_annotations:
        v = obj.bounding_poly.normalized_vertices
        detections.append({
            "class": obj.name.lower(),
            "confidence": round(obj.score * 100, 2),
            "bounding_box": {
                "x": v[0].x, "y": v[0].y,
                "width": v[2].x - v[0].x, "height": v[2].y - v[0].y
            }
        })
        class_summary[obj.name.lower()] = class_summary.get(obj.name.lower(), 0) + 1
    return {"detections": detections, "class_summary": class_summary, "total": len(detections)}
```

Add to requirements.txt: `google-cloud-vision>=3.7.0`

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Cloud Vision API           | 1k units free/month   | $0 (free tier)     |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$11–17/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete objdetect-repo --location=$GCP_REGION --quiet
gcloud projects delete objdetect-cv-project
```
