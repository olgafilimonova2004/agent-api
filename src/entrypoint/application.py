from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager

from dishka import Container
from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.clients.lm_client import LMClient
from src.entrypoint.container import setup_di
from src.models.config import AppConfig
from src.services.embedder import EmbedderService
from src.services.vespa import VespaService


class Application:
    def __init__(
        self,
        config: AppConfig,
        routers: list[APIRouter],
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
            app.include_router(router)

    def start_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            async with AsyncExitStack() as stack:
                for client_type in (LMClient, EmbedderService, VespaService):
                    stack.push_async_callback(self.container.get(client_type).close)
                yield

        app = FastAPI(lifespan=lifespan)

        setup_di(container=self.container, app=app)

        self.initialize(app=app)
        return app
