import logging

from fastapi import APIRouter

from src.common.enums import RoutersMetainfo


class HealthCheckFilter(logging.Filter):
    EXCLUDED_PATHS = ("/healthcheck", "/ping")

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return all(path not in message for path in self.EXCLUDED_PATHS)


class HealthRouter:
    def __init__(self):
        tags = RoutersMetainfo.HEALTH_TAGS.value
        prefix = RoutersMetainfo.DEFAULT_PREFIX.value
        self.api_router = APIRouter(prefix=prefix, tags=list(tags))
        self._register(self.api_router)

    def _register(self, router: APIRouter) -> None:
        logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())

        @router.get("/ping")
        async def ping() -> str:
            return "pong"

        @router.get("/health")
        async def healthcheck() -> dict:
            return {"status": "ok"}
