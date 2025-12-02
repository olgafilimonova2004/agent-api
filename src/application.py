from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger
from dishka import Container

from src.models.config import AppConfig
from src.interfaces.router import BaseRouter
from src.common.database.postgres import PostgresPool
from src.common.container import setup_di


class Application:
    def __init__(
        self,
        config: AppConfig,
        routers: list[BaseRouter],
        container: Container,
    ):
        self._config = config
        self.routers = routers
        self.container = container

    def initialize(self, app: FastAPI) -> None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        for router in self.routers:
            app.include_router(
                router.router,
                prefix=router.prefix,
                tags=router.tags,
            )

    def start_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            try:
                db = self.container.get(PostgresPool)
                await db.create_pool()
                yield
            finally:
                logger.warning("Ending ")
                await db.close_pool()

        app = FastAPI(lifespan=lifespan)

        setup_di(container=self.container, app=app)

        self.initialize(app=app)
        return app