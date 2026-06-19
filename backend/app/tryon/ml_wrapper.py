import httpx
import base64
import hashlib
import logging
from typing import Optional
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

INTERNAL_NGINX_URL = "http://nginx:80"

RESULTS_DIR = Path("/app/static/tryon_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

HEALTHCHECK_TIMEOUT = 5.0
IMAGE_DOWNLOAD_TIMEOUT = 15.0


class CatVTONClient:

    def __init__(self):
        self.base_url = settings.CATVTON_API_URL.rstrip("/")
        self.timeout = float(settings.CATVTON_TIMEOUT)
        self.enabled = settings.CATVTON_ENABLED
        self.fallback_image = settings.CATVTON_FALLBACK_IMAGE

    def _make_absolute_url(self, url: str) -> str:
        if not url:
            return url
        if url.startswith("http://") or url.startswith("https://"):
            return url
        clean_path = url.lstrip("/")
        return f"{INTERNAL_NGINX_URL}/{clean_path}"

    def _make_fallback(self, error: Optional[str] = None) -> dict:
        return {
            "result_image_url": self.fallback_image,
            "error": error,
            "fallback": True,
        }

    def _compute_cache_key(
            self,
            person_url: str,
            garment_url: str,
            mask_url: Optional[str] = None,
            category: str = "upper_body"
    ) -> str:
        payload = f"{person_url}|{garment_url}|{mask_url or ''}|{category}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def _get_cached_result(self, cache_key: str) -> Optional[str]:
        for ext in ("png", "jpg", "jpeg"):
            candidate = RESULTS_DIR / f"result_{cache_key}.{ext}"
            if candidate.exists() and candidate.stat().st_size > 0:
                cached_url = f"/static/tryon_results/{candidate.name}"
                logger.info(f"Cache hit for key {cache_key}: {cached_url}")
                return cached_url
        return None

    async def _check_health(self, client: httpx.AsyncClient) -> bool:
        try:
            resp = await client.get(
                f"{self.base_url}/health",
                timeout=HEALTHCHECK_TIMEOUT,
            )
            if resp.status_code != 200:
                logger.warning(f"Healthcheck returned status {resp.status_code}")
                return False
            data = resp.json()
            if not data.get("model_loaded", False):
                logger.warning("ML model is not loaded yet")
                return False
            return True
        except Exception as e:
            logger.warning(f"Healthcheck failed: {e}")
            return False

    async def _download_image(
            self, client: httpx.AsyncClient, url: str, label: str
    ) -> bytes:
        try:
            resp = await client.get(url, timeout=IMAGE_DOWNLOAD_TIMEOUT)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise ValueError(
                    f"Invalid content-type for {label}: {content_type}"
                )
            if len(resp.content) == 0:
                raise ValueError(f"Empty image data for {label}")
            return resp.content
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to download {label}: {e}")

    async def run_tryon(
            self,
            person_img_url: str,
            garment_img_url: str,
            mask_img_url: Optional[str] = None,
            category: str = "upper_body"
    ) -> dict:
        logger.info(
            f"Starting try-on: person={person_img_url}, "
            f"garment={garment_img_url}, mask={mask_img_url}"
        )
        if not self.enabled:
            logger.warning("CatVTON is disabled in configuration")
            return self._make_fallback("ML service disabled by config")
        cache_key = self._compute_cache_key(person_img_url, garment_img_url, mask_img_url, category)
        cached = self._get_cached_result(cache_key)
        if cached:
            return {
                "result_image_url": cached,
                "error": None,
                "fallback": False,
            }
        async with httpx.AsyncClient() as client:
            if not await self._check_health(client):
                error_msg = "ML service healthcheck failed"
                logger.error(error_msg)
                return self._make_fallback(error_msg)
            abs_person_url = self._make_absolute_url(person_img_url)
            abs_garment_url = self._make_absolute_url(garment_img_url)
            abs_mask_url = self._make_absolute_url(mask_img_url) if mask_img_url else None
            try:
                person_bytes = await self._download_image(
                    client, abs_person_url, "person"
                )
                garment_bytes = await self._download_image(
                    client, abs_garment_url, "garment"
                )
            except ValueError as e:
                logger.error(str(e))
                return self._make_fallback(str(e))
            files = {
                "person_image": ("person.jpg", person_bytes, "image/jpeg"),
                "garment_image": ("garment.jpg", garment_bytes, "image/jpeg"),
            }
            data = {"category": category, "num_inference_steps": "30"}
            if abs_mask_url:
                try:
                    mask_bytes = await self._download_image(
                        client, abs_mask_url, "mask"
                    )
                    files["mask_image"] = ("mask.png", mask_bytes, "image/png")
                except ValueError as e:
                    logger.warning(f"Mask download skipped: {e}")
            try:
                response = await client.post(
                    f"{self.base_url}/predict",
                    files=files,
                    data=data,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
            except httpx.TimeoutException:
                error_msg = f"Inference timeout after {self.timeout}s"
                logger.error(error_msg)
                return self._make_fallback(error_msg)
            except httpx.ConnectError:
                error_msg = "Cannot connect to ML service"
                logger.error(error_msg)
                return self._make_fallback(error_msg)
            except httpx.HTTPStatusError as e:
                error_msg = (
                    f"ML service HTTP {e.response.status_code}: "
                    f"{e.response.text[:200]}"
                )
                logger.error(error_msg)
                return self._make_fallback(error_msg)
            except httpx.HTTPError as e:
                error_msg = f"ML service network error: {e}"
                logger.error(error_msg)
                return self._make_fallback(error_msg)
            try:
                if payload.get("status") != "success":
                    error_msg = (
                        f"ML service reported failure: "
                        f"{payload.get('error', 'unknown')}"
                    )
                    logger.error(error_msg)
                    return self._make_fallback(error_msg)
                if "result_image_base64" in payload:
                    img_bytes = base64.b64decode(payload["result_image_base64"])
                    fmt = payload.get("format", "png")
                    filename = f"result_{cache_key}.{fmt}"
                    result_path = RESULTS_DIR / filename
                    with open(result_path, "wb") as f:
                        f.write(img_bytes)
                    result_url = f"/static/tryon_results/{filename}"
                    logger.info(f"Try-on completed successfully: {result_url}")
                    return {
                        "result_image_url": result_url,
                        "error": None,
                        "fallback": False,
                    }
                elif "result_image_url" in payload:
                    result_url = payload["result_image_url"]
                    logger.info(f"Try-on completed (remote URL): {result_url}")
                    return {
                        "result_image_url": result_url,
                        "error": None,
                        "fallback": False,
                    }
                else:
                    raise ValueError(
                        f"Unsupported ML response structure. "
                        f"Keys: {list(payload.keys())}"
                    )
            except ValueError as e:
                error_msg = f"Invalid ML response: {e}"
                logger.error(error_msg)
                return self._make_fallback(error_msg)
            except Exception as e:
                error_msg = f"Result processing error: {type(e).__name__}: {e}"
                logger.error(error_msg, exc_info=True)
                return self._make_fallback(error_msg)
