from typing import Union
import asyncio

import asyncpg
from asyncpg.pool import Pool
from loguru import logger

from src.models.config import PostgresConfig


class PostgresPool:
    def __init__(self, config: PostgresConfig):
        self.pool: Union[Pool, None] = None
        self._config = config

    async def create_pool(self) -> Pool:
        connection_attempt = 0

        if not self.pool:
            while connection_attempt < self._config.MAX_CONN_ATTEMPT:
                try:
                    self.pool = await asyncpg.create_pool(
                        dsn=self._config.DSN,
                        min_size=self._config.MIN_SIZE,
                        max_size=self._config.MAX_SIZE,
                    )
                    logger.success("Successfully connected to database")
                    return self.pool

                except Exception as e:
                    connection_attempt += 1
                    logger.warning(
                        f"Trying to connect to the database. Connection attempt: {connection_attempt}/{self._config.MAX_CONN_ATTEMPT}. Error: {e}"
                    )
                    logger.debug(f"DSN: {self._config.DSN}")
                    if connection_attempt < self._config.MAX_CONN_ATTEMPT:
                        await asyncio.sleep(connection_attempt * 2)

            raise asyncpg.exceptions.PostgresConnectionError(
                f"Failed to connect to database after {self._config.MAX_CONN_ATTEMPT} attempts"
            )

    async def close_pool(self) -> None:
        if self.pool:
            try:
                await self.pool.close()
                logger.info("Database pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing database pool: {e}")
            finally:
                self.pool = None
        else:
            logger.info("Active pool was closed or not found")