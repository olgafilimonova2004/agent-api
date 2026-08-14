from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
from asyncpg.pool import Pool
from loguru import logger

from src.common.decorators import retry_policy
from src.models.config import PostgresConfig


class PostgresPool:
    def __init__(self, config: PostgresConfig):
        self._pool: Pool | None = None
        self._config = config

        @retry_policy(self._config.MAX_CONN_ATTEMPT, OSError)
        async def create_pool() -> Pool:
            if not self._pool:
                self._pool = await asyncpg.create_pool(
                    dsn=self._config.DSN,
                    min_size=self._config.MIN_SIZE,
                    max_size=self._config.MAX_SIZE,
                )
                logger.success("Successfully connected to database")
                return self._pool
            else:
                return self._pool

        self.create_pool = create_pool

    @property
    def pool(self) -> Pool:
        if self._pool is None:
            raise RuntimeError("Database Pool not inilialized")
        return self._pool

    async def close_pool(self) -> None:
        if self._pool:
            try:
                await self._pool.close()
                logger.info("Database pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing database pool: {e}")
            finally:
                self._pool = None
        else:
            logger.info("Active pool was closed or not found")

    @asynccontextmanager
    async def tx(self) -> AsyncGenerator[asyncpg.Connection]:
        async with self.pool.acquire() as conn, conn.transaction():
            yield conn

    async def fetch(
        self, query: str, *args: Any, **kwargs: Any
    ) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args, **kwargs)

    async def fetchrow(
        self, query: str, *args: Any, **kwargs: Any
    ) -> asyncpg.Record | None:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args, **kwargs)

    async def fetchval(self, query: str, *args: Any, **kwargs: Any) -> Any:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args, **kwargs)

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> str:
        """:return str: Status of the last SQL command."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args, **kwargs)
