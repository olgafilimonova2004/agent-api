from http import HTTPStatus

from fastapi import APIRouter, Response

from src.common.enums import RoutersMetainfo
from src.interfaces.router import BaseRouter
from src.services.example import ExampleService


class ExampleRouter(BaseRouter):
    def __init__(
        self,
        example_service: ExampleService,
    ):
        self.example_service = example_service
        self.tags = RoutersMetainfo.DEFAULT_TAGS.value
        self.prefix = RoutersMetainfo.DEFAULT_PREFIX.value

    @property
    def router(self) -> APIRouter:
        router = APIRouter()
        self.initialize(router)

        return router

    def initialize(self, router: APIRouter) -> None:
        @router.get("/ping")
        async def ping() -> str:
            return "pong"

        @router.get("/ready")
        async def ready() -> dict:
            return {"status": "ok"}
