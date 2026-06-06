import httpx
import uuid
import logging
from typing import Optional
from app.core.config import settings
from app.payments.exceptions import YooKassaAPIError, YooKassaConfigError

logger = logging.getLogger(__name__)


class YooKassaClient:
    """Асинхронный клиент для работы с API ЮKassa."""

    BASE_URL = "https://api.yookassa.ru/v3"

    def __init__(self):
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.secret_key = settings.YOOKASSA_SECRET_KEY

        if not self.shop_id or not self.secret_key:
            logger.warning(
                "YooKassa credentials not configured. "
                "Payment operations will fail."
            )

    def _get_headers(self, idempotence_key: Optional[str] = None) -> dict:
        """Формирует заголовки для запроса."""
        headers = {
            "Content-Type": "application/json",
        }
        if idempotence_key:
            headers["Idempotence-Key"] = idempotence_key
        return headers

    def _get_auth(self) -> tuple:
        """Возвращает tuple для Basic Auth."""
        if not self.shop_id or not self.secret_key:
            raise YooKassaConfigError(
                "YooKassa shop_id and secret_key are required"
            )
        return (self.shop_id, self.secret_key)

    async def create_payment(
            self,
            amount: float,
            description: str,
            order_id: str,
            metadata: Optional[dict] = None,
            return_url: Optional[str] = None,
            cancel_url: Optional[str] = None,
    ) -> dict:
        """
        Создает платеж в ЮKassa.
        Возвращает ответ от API в формате JSON.
        """
        url = f"{self.BASE_URL}/payments"
        idempotence_key = str(uuid.uuid4())

        payment_data = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": return_url or settings.YOOKASSA_RETURN_URL,
                "cancel_url": cancel_url or settings.YOOKASSA_CANCEL_URL,
            },
            "description": description[:128],
            "metadata": metadata or {"order_id": order_id},
        }

        logger.info(
            f"Creating YooKassa payment for order {order_id}, "
            f"amount: {amount}"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payment_data,
                    auth=self._get_auth(),
                    headers=self._get_headers(idempotence_key)
                )
                response.raise_for_status()
                result = response.json()
                logger.info(
                    f"YooKassa payment created: {result.get('id')}, "
                    f"status: {result.get('status')}"
                )
                return result
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(
                f"YooKassa API HTTP error: "
                f"{e.response.status_code} - {error_text}"
            )
            raise YooKassaAPIError(f"API error: {error_text}")
        except httpx.RequestError as e:
            logger.error(f"YooKassa API request error: {e}")
            raise YooKassaAPIError(f"Request error: {str(e)}")

    async def get_payment(self, payment_id: str) -> dict:
        """Получает информацию о платеже по его ID в ЮKassa."""
        url = f"{self.BASE_URL}/payments/{payment_id}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    auth=self._get_auth(),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"YooKassa get payment error: {e.response.status_code}"
            )
            raise YooKassaAPIError(f"API error: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"YooKassa request error: {e}")
            raise YooKassaAPIError(f"Request error: {str(e)}")

    async def create_refund(
            self,
            payment_id: str,
            amount: float,
            description: Optional[str] = None,
    ) -> dict:
        """
        Создаёт возврат средств через YooKassa API.
        Используется при одобрении заявки на возврат товара.
        """
        url = f"{self.BASE_URL}/refunds"
        idempotence_key = str(uuid.uuid4())

        refund_data = {
            "payment_id": payment_id,
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
        }

        if description:
            refund_data["description"] = description[:128]

        logger.info(
            f"Creating YooKassa refund for payment {payment_id}, "
            f"amount: {amount}"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=refund_data,
                    auth=self._get_auth(),
                    headers=self._get_headers(idempotence_key)
                )
                response.raise_for_status()
                result = response.json()

                logger.info(
                    f"YooKassa refund created: {result.get('id')}, "
                    f"status: {result.get('status')}"
                )
                return result

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(
                f"YooKassa refund API error: "
                f"{e.response.status_code} - {error_text}"
            )
            raise YooKassaAPIError(f"Refund API error: {error_text}")
        except httpx.RequestError as e:
            logger.error(f"YooKassa refund request error: {e}")
            raise YooKassaAPIError(f"Refund request error: {str(e)}")

    async def cancel_payment(self, payment_id: str) -> dict:
        """Отменяет платеж."""
        url = f"{self.BASE_URL}/payments/{payment_id}/cancel"
        idempotence_key = str(uuid.uuid4())

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    auth=self._get_auth(),
                    headers=self._get_headers(idempotence_key)
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"YooKassa cancel error: {e.response.status_code}"
            )
            raise YooKassaAPIError(f"API error: {e.response.text}")


# Глобальный экземпляр клиента
yookassa_client = YooKassaClient()
