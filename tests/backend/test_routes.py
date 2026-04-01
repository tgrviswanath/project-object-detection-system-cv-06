from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "object_count": 2,
    "detections": [
        {"label": "person", "confidence": 87.5, "x": 100, "y": 80, "width": 200, "height": 170, "class_id": 0},
        {"label": "car", "confidence": 72.3, "x": 300, "y": 200, "width": 150, "height": 100, "class_id": 2},
    ],
    "class_summary": {"person": 1, "car": 1},
    "image_width": 640, "image_height": 480,
    "annotated_image": "base64string",
    "model": "yolov8n.pt",
}
MOCK_MODEL_INFO = {"model": "yolov8n.pt", "confidence_threshold": 0.4, "classes": "80 COCO classes"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.detect_objects", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_detect_endpoint(mock_detect):
    r = client.post("/api/v1/detect",
        files={"file": ("test.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert data["object_count"] == 2
    assert data["class_summary"]["person"] == 1


@patch("app.core.service.get_model_info", new_callable=AsyncMock, return_value=MOCK_MODEL_INFO)
def test_model_info_endpoint(mock_info):
    r = client.get("/api/v1/model-info")
    assert r.status_code == 200
    assert r.json()["model"] == "yolov8n.pt"
