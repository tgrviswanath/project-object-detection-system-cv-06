from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (640, 480), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _mock_yolo_result():
    result = MagicMock()
    box = MagicMock()
    box.xyxy = [MagicMock()]
    box.xyxy[0].tolist.return_value = [100.0, 80.0, 300.0, 250.0]
    box.conf = [MagicMock()]
    box.conf[0].__float__ = lambda self: 0.87
    box.cls = [MagicMock()]
    box.cls[0].__int__ = lambda self: 0
    result.boxes = [box]
    result.names = {0: "person"}
    return [result]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_model_info():
    r = client.get("/api/v1/cv/model-info")
    assert r.status_code == 200
    assert "model" in r.json()


@patch("app.core.detector._get_model")
def test_detect(mock_get_model):
    mock_model = MagicMock()
    mock_model.return_value = _mock_yolo_result()
    mock_model.names = {0: "person"}
    mock_get_model.return_value = mock_model

    r = client.post("/api/v1/cv/detect",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert "object_count" in data
    assert "detections" in data
    assert "annotated_image" in data
    assert "class_summary" in data


def test_unsupported_format():
    r = client.post("/api/v1/cv/detect",
        files={"file": ("test.gif", b"GIF89a", "image/gif")})
    assert r.status_code == 400


def test_empty_file():
    r = client.post("/api/v1/cv/detect",
        files={"file": ("test.jpg", b"", "image/jpeg")})
    assert r.status_code == 400
