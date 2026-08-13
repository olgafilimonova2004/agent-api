import logging

from fastapi import APIRouter

from src.common.enums import RoutersMetainfo
from src.interfaces.router import IBaseRouter


class HealthCheckFilter(logging.Filter):
    EXCLUDED_PATHS = ("/healthcheck", "/ping")

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return all(path not in message for path in self.EXCLUDED_PATHS)


class HealthRouter(IBaseRouter):
    def __init__(self):
        self._tags = RoutersMetainfo.HEALTH_TAGS.value
        self._base_prefix = RoutersMetainfo.DEFAULT_PREFIX.value

    def _register(self, router: APIRouter) -> None:
        logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())

        @router.get("/ping")
        async def ping() -> str:
            return "pong"

        @router.get("/health")
        async def healthcheck() -> dict:
            return {"status": "ok"}
