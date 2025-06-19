from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.models.config import AppConfig
from src.routers.default import DefaultRouter


class Application():
    def __init__(
        self,
        config: AppConfig,
        default: DefaultRouter,
    ):
        self._config = config
        self._default = default
    
    def setup(self, server: FastAPI) -> None:
        server.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentiald=True,
            allow_methods=['*'],
            allow_headers=['*']
        )
        server.include_router(self._default.api_router, prefix=self._default.base_prefix, tags=self._default.tags)
    
    def start_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(server: FastAPI) -> AsyncGenerator[None, None]:
            try:
                await db.connect()
                yield
            finally:
                await db.disconnect
        
        server = FastAPI(lifespan=lifespan)
        self.setup(server=server)
        return server