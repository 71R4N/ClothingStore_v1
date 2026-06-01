import httpx
from typing import Optional
from app.core.config import settings

class CatVTONClient:
    def __init__(self, base_url: str = settings.CATVTON_MODEL_PATH):
        self.base_url = base_url.rstrip("/")

    async def run_tryon(self, person_img_url: str, garment_img_url: str, mask_img_url: Optional[str] = None) -> dict:
        print(f"[ML_WRAPPER] Начало run_tryon. person_img_url={person_img_url}, garment_img_url={garment_img_url}")
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                print(f"[ML_WRAPPER] Скачиваю person_img: {person_img_url}")
                person_resp = await client.get(person_img_url)
                print(f"[ML_WRAPPER] person_resp status: {person_resp.status_code}")
                print(f"[ML_WRAPPER] Скачиваю garment_img: {garment_img_url}")
                garment_resp = await client.get(garment_img_url)
                print(f"[ML_WRAPPER] garment_resp status: {garment_resp.status_code}")
                if person_resp.status_code != 200 or garment_resp.status_code != 200:
                    return {"result_image_url": None, "error": "Failed to download images"}
            except Exception as e:
                print(f"[ML_WRAPPER] Ошибка скачивания: {e}")
                return {"result_image_url": None, "error": f"Download error: {str(e)}"}
            files = {
                "person_image": ("person.jpg", person_resp.content, "image/jpeg"),
                "garment_image": ("garment.jpg", garment_resp.content, "image/jpeg"),
            }
            if mask_img_url:
                try:
                    mask_resp = await client.get(mask_img_url)
                    if mask_resp.status_code == 200:
                        files["mask_image"] = ("mask.png", mask_resp.content, "image/png")
                except Exception:
                    pass
            try:
                response = await client.post(f"{self.base_url}/tryon", files=files)
                response.raise_for_status()
                data = response.json()
                if "result_image_base64" in data:
                    import base64
                    import os
                    img_data = base64.b64decode(data["result_image_base64"])
                    os.makedirs("/app/static/tryon_results", exist_ok=True)
                    result_filename = f"result_{hash(person_img_url)}.png"
                    result_path = f"/app/static/tryon_results/{result_filename}"
                    with open(result_path, "wb") as f:
                        f.write(img_data)
                    print(f"[ML_WRAPPER] Response status: {response.status_code}")
                    print(f"[ML_WRAPPER] Response text (first 500 chars): {response.text[:500]}")
                    return {"result_image_url": f"/tryon_results/{result_filename}", "error": None}
                elif "result_image_url" in data:
                    return {"result_image_url": data["result_image_url"], "error": None}
                else:
                    return {"result_image_url": None, "error": "No result found in response"}
            except Exception as e:
                return {"result_image_url": None, "error": str(e)}


# import httpx
# import asyncio
# from app.core.config import settings
#
# class CatVTONClient:
#     def __init__(self, base_url: str = settings.CATVTON_MODEL_PATH):
#         self.base_url = base_url.rstrip("/")
#
#     async def run_tryon(self, person_img_url: str, garment_img_url: str, mask_img_url: str | None = None) -> dict:
#         """
#         Отправляет запрос к CatVTON API (Google Colab) и возвращает результат.
#         Ожидается, что Colab предоставляет REST API с эндпоинтом /tryon.
#         """
#         async with httpx.AsyncClient(timeout=300.0) as client:
#             payload = {
#                 "person_image": person_img_url,
#                 "garment_image": garment_img_url,
#                 "mask_image": mask_img_url
#             }
#             try:
#                 response = await client.post(f"{self.base_url}/tryon", json=payload)
#                 response.raise_for_status()
#                 data = response.json()
#                 return {"result_image_url": data.get("result_image_url"), "error": None}
#             except Exception as e:
#                 return {"result_image_url": None, "error": str(e)}
#