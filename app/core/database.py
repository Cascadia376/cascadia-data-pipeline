import asyncpg
from .config import settings

class Database:
    def __init__(self):
        self._pool = None

    async def connect(self):
        self._pool = await asyncpg.create_pool(dsn=settings.database_url)

    async def disconnect(self):
        if self._pool:
            await self._pool.close()

    @property
    def pool(self):
        return self._pool

db = Database()
