from fastapi import APIRouter

from src.common.enums import RoutersMetainfo
from src.interfaces.router import IBaseRouter
from src.services.example import ExampleService


class ExampleRouter(IBaseRouter):
    def __init__(
        self,
        example_service: ExampleService,
    ):
        self.example_service = example_service
        self._tags = RoutersMetainfo.EXAMPLE_TAGS.value
        self._base_prefix = RoutersMetainfo.DEFAULT_PREFIX.value

    def _register(self, router: APIRouter) -> None:
        @router.get("/")
        async def get_all_data():
            return await self.example_service.get_all()

        @router.post("/query_other_service")
        async def get_something_from_other_service(data: dict):
            return await self.example_service.get_something_from_other_service(data)
