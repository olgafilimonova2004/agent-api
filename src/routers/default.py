from http import HTTPStatus

from fastapi import APIRouter, Response

from src.common.database.postgres import psql as db
from src.interfaces.router import BaseRouter
from src.services.example import ExampleService


class DefaultRouter(BaseRouter):
    def __init__(
        self,
        example_service: ExampleService,
        base_prefix: str = "",
        tags: list[str] | None = None,
    ):
        self.example_service = example_service
        self._base_prefix = base_prefix
        self._tags = tags or []

    @property
    def tags(self) -> list[str]:
        return self._tags

    @property
    def base_prefix(self) -> str:
        return self._base_prefix

    @property
    def api_router(self) -> APIRouter:
        server = APIRouter()
        self._register(server)
        return server

    def _register(self, router: APIRouter) -> None:
        @router.get("/ping")
        async def ping() -> str:
            return "pong"

        @router.get("/ready")
        async def ready(response: Response) -> dict:

            return {"status": "ok"}
