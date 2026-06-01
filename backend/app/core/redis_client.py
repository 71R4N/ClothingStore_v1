import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = await redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def setex(self, key: str, seconds: int, value: str):
        await self.client.setex(key, seconds, value)

    async def delete(self, key: str):
        await self.client.delete(key)

# Глобальный экземпляр
redis_client = RedisClient()
