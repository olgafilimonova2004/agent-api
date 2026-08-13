import asyncpg
from asyncpg.pool import Pool
from loguru import logger

from src.common.decorators import retry_policy
from src.models.config import PostgresConfig


class PostgresPool:
    def __init__(self, config: PostgresConfig):
        self._pool: Pool | None = None
        self._config = config

    @retry_policy(5, OSError)
    async def create_pool(self) -> Pool:
        connection_attempt = 0

        if not self._pool:
            while connection_attempt < self._config.MAX_CONN_ATTEMPT:
                self._pool = await asyncpg.create_pool(
                    dsn=self._config.DSN,
                    min_size=self._config.MIN_SIZE,
                    max_size=self._config.MAX_SIZE,
                )
                logger.success("Successfully connected to database")
                return self._pool

            raise asyncpg.exceptions.PostgresConnectionError(
                f"Failed to connect to database after {self._config.MAX_CONN_ATTEMPT} attempts"
            )
        else:
            return self._pool

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
