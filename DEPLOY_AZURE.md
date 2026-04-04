# Azure Deployment Guide — Project CV-06 Object Detection System

---

## Azure Services for Object Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Vision — Object Detection**| Detect objects with bounding boxes and confidence scores                    | Replace your YOLOv8 pipeline                       |
| **Azure Custom Vision**              | Train a custom object detector on your labelled images — no code needed      | When you need domain-specific object categories    |
| **Azure OpenAI Vision**              | GPT-4V for custom object detection and scene understanding via prompt        | When you need flexible object detection            |

> **Azure AI Vision Object Detection** is the direct replacement for your YOLOv8 pipeline. It returns bounding boxes + confidence for common objects — no model download needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Train and Manage Your Model

| Service                        | What it does                                                              | When to use                                           |
|--------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Custom Vision**        | Train custom object detector via UI — no code needed                      | When you need custom COCO-style categories            |
| **Azure Machine Learning**     | Fine-tune YOLOv8 on custom datasets, deploy managed endpoints             | Full ML pipeline for custom object detection          |

### 4. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 5. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images and annotated detection results                    |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track detection latency, object counts, request volume               |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure AI Vision Object Detection   │
│ CV Service :8001  │    │ or Azure Custom Vision             │
│ YOLOv8 nano       │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-obj-detection --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-obj-detection --name objdetectacr --sku Basic --admin-enabled true
az acr login --name objdetectacr
ACR=objdetectacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name objdetect-env --resource-group rg-obj-detection --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-obj-detection \
  --environment objdetect-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-obj-detection \
  --environment objdetect-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure AI Vision Object Detection

```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

client = ImageAnalysisClient(
    endpoint=os.getenv("AZURE_VISION_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_VISION_KEY"))
)

def detect_objects(image_bytes: bytes) -> dict:
    result = client.analyze(
        image_data=image_bytes,
        visual_features=[VisualFeatures.OBJECTS]
    )
    detections, class_summary = [], {}
    if result.objects:
        for obj in result.objects.list:
            rect = obj.bounding_box
            detections.append({
                "class": obj.tags[0].name if obj.tags else "unknown",
                "confidence": round(obj.tags[0].confidence * 100, 2) if obj.tags else 0,
                "bounding_box": {"x": rect.x, "y": rect.y, "w": rect.width, "h": rect.height}
            })
            cls = obj.tags[0].name if obj.tags else "unknown"
            class_summary[cls] = class_summary.get(cls, 0) + 1
    return {"detections": detections, "class_summary": class_summary, "total": len(detections)}
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure AI Vision          | F0 free   | $0 (5k calls)     |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–20/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-obj-detection --yes --no-wait
```
