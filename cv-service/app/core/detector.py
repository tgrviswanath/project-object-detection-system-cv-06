"""
YOLOv8 object detector.
- Model auto-downloaded by ultralytics on first run (~6MB for nano)
- Returns: detections list + annotated image (base64) + class summary
"""
import cv2
import numpy as np
from PIL import Image
import io
import base64
from app.core.config import settings

_model = None


def _get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        _model = YOLO(settings.YOLO_MODEL)
    return _model


def _load_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > settings.MAX_IMAGE_SIZE:
        scale = settings.MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return np.array(img)


def _to_base64(img_rgb: np.ndarray) -> str:
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buf).decode("utf-8")


def detect(image_bytes: bytes) -> dict:
    model = _get_model()
    img = _load_image(image_bytes)
    h, w = img.shape[:2]

    results = model(img, conf=settings.CONFIDENCE_THRESHOLD, verbose=False)[0]

    detections = []
    annotated = img.copy()

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = round(float(box.conf[0]), 4)
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        detections.append({
            "label": label,
            "confidence": round(conf * 100, 2),
            "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1,
            "class_id": cls_id,
        })

        # Draw bounding box
        color = (0, 255, 0)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        text = f"{label} {round(conf * 100, 1)}%"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
        cv2.putText(annotated, text, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    # Class summary
    summary = {}
    for d in detections:
        summary[d["label"]] = summary.get(d["label"], 0) + 1

    detections.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "object_count": len(detections),
        "detections": detections,
        "class_summary": summary,
        "image_width": w,
        "image_height": h,
        "annotated_image": _to_base64(annotated),
        "model": settings.YOLO_MODEL,
    }
