import httpx
from app.core.config import settings

CV_URL = settings.CV_SERVICE_URL


async def detect_objects(filename: str, content: bytes, content_type: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CV_URL}/api/v1/cv/detect",
            files={"file": (filename, content, content_type)},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json()


async def get_model_info() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{CV_URL}/api/v1/cv/model-info", timeout=10.0)
        r.raise_for_status()
        return r.json()
