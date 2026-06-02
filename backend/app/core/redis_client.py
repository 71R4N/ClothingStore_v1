import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        try:
            self.client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.client.ping()  # Проверяем соединение
        except redis.ConnectionError as e:
            self.client = None  # Приложение продолжит работу без redis

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def setex(self, key: str, seconds: int, value: str):
        await self.client.setex(key, seconds, value)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def disconnect(self):
        if self.client:
            await self.client.close()

# Глобальный экземпляр
redis_client = RedisClient()
