import httpx
import base64
import os
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class CatVTONClient:
    def __init__(self):
        self.base_url = settings.CATVTON_API_URL.rstrip("/")
        self.timeout = settings.CATVTON_TIMEOUT
        self.enabled = settings.CATVTON_ENABLED
        self.fallback_image = settings.CATVTON_FALLBACK_IMAGE

    async def run_tryon(
            self,
            person_img_url: str,
            garment_img_url: str,
            mask_img_url: Optional[str] = None
    ) -> dict:
        """
        Запускает виртуальную примерку через CatVTON API.
        Возвращает {"result_image_url": str, "error": str | None}
        """
        logger.info(f"Starting try-on: person={person_img_url}, garment={garment_img_url}")

        # Если сервис отключен — возвращаем fallback
        if not self.enabled:
            logger.warning("CatVTON is disabled, using fallback image")
            return {
                "result_image_url": self.fallback_image,
                "error": None,
                "fallback": True
            }

        async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
            # Скачиваем изображения
            try:
                person_resp = await client.get(person_img_url)
                garment_resp = await client.get(garment_img_url)

                if person_resp.status_code != 200 or garment_resp.status_code != 200:
                    error_msg = f"Failed to download images: person={person_resp.status_code}, garment={garment_resp.status_code}"
                    logger.error(error_msg)
                    return {"result_image_url": self.fallback_image, "error": error_msg, "fallback": True}
            except Exception as e:
                error_msg = f"Download error: {str(e)}"
                logger.error(error_msg)
                return {"result_image_url": self.fallback_image, "error": error_msg, "fallback": True}

            # Подготавливаем файлы для отправки
            files = {
                "person_image": ("person.jpg", person_resp.content, "image/jpeg"),
                "garment_image": ("garment.jpg", garment_resp.content, "image/jpeg"),
            }

            if mask_img_url:
                try:
                    mask_resp = await client.get(mask_img_url)
                    if mask_resp.status_code == 200:
                        files["mask_image"] = ("mask.png", mask_resp.content, "image/png")
                except Exception as e:
                    logger.warning(f"Failed to download mask: {e}")

            # Отправляем запрос к CatVTON API
            try:
                response = await client.post(f"{self.base_url}/tryon", files=files)
                response.raise_for_status()
                data = response.json()

                # Обрабатываем результат
                if "result_image_base64" in data:
                    # Если вернул base64 — сохраняем локально
                    img_data = base64.b64decode(data["result_image_base64"])
                    result_filename = f"result_{hash(person_img_url)}_{hash(garment_img_url)}.png"
                    result_path = f"/app/static/tryon_results/{result_filename}"

                    os.makedirs("/app/static/tryon_results", exist_ok=True)
                    with open(result_path, "wb") as f:
                        f.write(img_data)

                    result_url = f"/static/tryon_results/{result_filename}"
                    logger.info(f"Try-on completed successfully: {result_url}")
                    return {"result_image_url": result_url, "error": None, "fallback": False}

                elif "result_image_url" in data:
                    # Если ML-сервис сам сохранил изображение и вернул URL
                    result_url = data["result_image_url"]
                    logger.info(f"Try-on completed successfully: {result_url}")
                    return {"result_image_url": result_url, "error": None, "fallback": False}
                else:
                    error_msg = "No result found in ML response"
                    logger.error(error_msg)
                    return {"result_image_url": self.fallback_image, "error": error_msg, "fallback": True}

            except httpx.TimeoutException:
                error_msg = f"CatVTON timeout after {self.timeout}s"
                logger.error(error_msg)
                return {"result_image_url": self.fallback_image, "error": error_msg, "fallback": True}
            except httpx.ConnectError:
                error_msg = "Cannot connect to CatVTON service"
                logger.error(error_msg)
                return {"result_image_url": self.fallback_image, "error": error_msg, "fallback": True}
            except Exception as e:
                error_msg = f"ML service error: {str(e)}"
                logger.error(error_msg)
                return {"result_image_url": self.fallback_image, "error": error_msg, "fallback": True}