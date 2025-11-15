import asyncio

import asyncpg
from asyncpg.pool import Pool
from loguru import logger


class Postgres:
    MAX_CONNECT_ATTEMPTS = 5
    CONNECTION_TIMEOUT = 30
    MIN_POOL_SIZE = 1
    MAX_POOL_SIZE = 10

    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool: Pool | None = None

    @property
    def pool(self) -> Pool:
        if not self._pool:
            raise RuntimeError("Connect to db first")

        return self._pool

    async def connect(self) -> Pool:
        if self._pool:
            return self._pool

        attempt = 0

        while attempt < self.MAX_CONNECT_ATTEMPTS:
            try:
                self._pool = await asyncpg.create_pool(
                    self.dsn,
                    min_size=self.MIN_POOL_SIZE,
                    max_size=self.MAX_POOL_SIZE,
                    command_timeout=self.CONNECTION_TIMEOUT,
                )
                logger.info("Successfully connected to database")
                return self._pool  # noqa: TRY300
            except Exception as e:
                logger.error(
                    f"Failed to connect to db (attempt {attempt + 1}/{self.MAX_CONNECT_ATTEMPTS}): {str(e)}"
                )
                attempt += 1
                await asyncio.sleep(2**attempt)

        raise ConnectionError("Could not connect to db")  # noqa: EM101, TRY003

    async def disconnect(self) -> None:
        if self._pool:
            try:
                await self._pool.close()
                self._pool = None
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
