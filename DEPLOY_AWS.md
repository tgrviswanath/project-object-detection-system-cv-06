# AWS Deployment Guide — Project CV-06 Object Detection System

---

## AWS Services for Object Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Rekognition**     | Detect objects, scenes, and activities — returns labels + bounding boxes     | Replace your YOLOv8 pipeline                       |
| **Amazon Rekognition**     | Supports 3000+ object categories with confidence scores                      | When you need broad object coverage                |
| **Amazon Bedrock**         | Claude Vision for custom object detection and scene understanding            | When you need domain-specific object detection     |

> **Amazon Rekognition DetectLabels** is the direct replacement for your YOLOv8 pipeline. It returns bounding boxes + confidence for 3000+ categories — no model download needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Train and Manage Your Model

| Service                         | What it does                                                        | When to use                                           |
|---------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS SageMaker**               | Fine-tune YOLOv8 on custom datasets, deploy managed endpoints       | When you need domain-specific object detection        |
| **Amazon Rekognition Custom**   | Train custom object detector on your labelled images                | When you need custom categories without code          |

### 4. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 5. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images and annotated detection results                     |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track detection latency, object counts, request volume                    |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Rekognition                 │
│ CV Service :8001  │    │ DetectLabels API                   │
│ YOLOv8 nano       │    │ 3000+ categories, no model needed  │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name objdetect/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name objdetect/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/objdetect/cv-service:latest ./cv-service
docker push $ECR/objdetect/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/objdetect/backend:latest ./backend
docker push $ECR/objdetect/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name objdetect-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/objdetect/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Rekognition

```python
import boto3

rekognition = boto3.client("rekognition", region_name="eu-west-2")

def detect_objects(image_bytes: bytes, confidence_threshold: float = 40.0) -> dict:
    response = rekognition.detect_labels(
        Image={"Bytes": image_bytes},
        MaxLabels=50,
        MinConfidence=confidence_threshold,
        Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"]
    )
    detections = []
    class_summary = {}
    for label in response["Labels"]:
        for instance in label.get("Instances", []):
            box = instance["BoundingBox"]
            detections.append({
                "class": label["Name"].lower(),
                "confidence": round(label["Confidence"], 2),
                "bounding_box": box
            })
            class_summary[label["Name"].lower()] = class_summary.get(label["Name"].lower(), 0) + 1
    return {"detections": detections, "class_summary": class_summary, "total": len(detections)}
```

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-2
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -f docker/Dockerfile.backend \
            -t ${{ secrets.ECR_REGISTRY }}/objdetect/backend:${{ github.sha }} ./backend
          docker push ${{ secrets.ECR_REGISTRY }}/objdetect/backend:${{ github.sha }}
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Rekognition         | 1M images free    | $0 (free tier)     |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$23–32/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name objdetect/backend --force
aws ecr delete-repository --repository-name objdetect/cv-service --force
```
