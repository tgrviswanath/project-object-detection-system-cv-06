from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.detector import detect
from app.core.config import settings

router = APIRouter(prefix="/api/v1/cv", tags=["object-detection"])

ALLOWED = {"jpg", "jpeg", "png", "bmp", "webp"}


def _validate(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}")


@router.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    _validate(file.filename)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    return detect(content)


@router.get("/model-info")
def model_info():
    return {
        "model": settings.YOLO_MODEL,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "classes": "80 COCO classes",
    }
