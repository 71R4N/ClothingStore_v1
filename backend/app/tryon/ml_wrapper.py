import httpx
import asyncio
from app.core.config import settings

class CatVTONClient:
    def __init__(self, base_url: str = settings.CATVTON_MODEL_PATH):
        self.base_url = base_url.rstrip("/")

    async def run_tryon(self, person_img_url: str, garment_img_url: str, mask_img_url: str | None = None) -> dict:
        """
        Отправляет запрос к CatVTON API (Google Colab) и возвращает результат.
        Ожидается, что Colab предоставляет REST API с эндпоинтом /tryon.
        """
        async with httpx.AsyncClient(timeout=300.0) as client:
            payload = {
                "person_image": person_img_url,
                "garment_image": garment_img_url,
                "mask_image": mask_img_url
            }
            try:
                response = await client.post(f"{self.base_url}/tryon", json=payload)
                response.raise_for_status()
                data = response.json()
                return {"result_image_url": data.get("result_image_url"), "error": None}
            except Exception as e:
                return {"result_image_url": None, "error": str(e)}
            