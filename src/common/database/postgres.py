from collections.abc import AsyncGenerator
from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_scoped_session
)

import loguru

from src.common.config import app_config


class DatabaseSessionManager:
    """
    Класс отвечающий за создание/удаление сессии и инициализацию базы данных
    """
    def __init__(self, db_url: str):
        self.engine: AsyncEngine | None = None
        self.session_marker = None
        self.session = None
        self._url = db_url

    def init_db(self):
        if self.engine is not None:
            raise Exception('Database already initialized')

        self.engine = create_async_engine(
            url=f'postgresql+asyncpg://{self._url}',
            pool_size=100, max_overflow=100, pool_pre_ping=True,
        )

        self.session_marker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        self.session = async_scoped_session(
            self.session_marker, scopefunc=current_task
        )
        loguru.logger.success('Database initialized')

    async def close(self):
        if self.engine is None:
            raise Exception('DatabaseSessionManager has not been initialized')
        await self.session.remove()
        await self.engine.dispose()


psql = DatabaseSessionManager(app_config.db_config.DB_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция get_db возвращает асинхронный генератор.
    Этот генератор можно использовать для получения объектов типа AsyncSession.
    """
    session = psql.session()
    if session is None:
        raise Exception('DatabaseSessionManager has not been initialized')
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()