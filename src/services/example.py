from loguru import logger

from src.clients.base_client import BaseClient
from src.common.errors import asyncpg_errors_decorator
from src.models.pydantic.example import ExampleData
from src.repositories.example_repository import ExampleRepository


class ExampleService:
    def __init__(
        self,
        client: BaseClient,
        repo: ExampleRepository,
    ):
        self.client = client
        self.repo = repo

    @asyncpg_errors_decorator
    async def get_all(self) -> list[ExampleData]:
        async with self.repo.db.tx() as tx:
            return await self.repo.get_all(conn=tx)

    async def get_something_from_other_service(self, json_data: dict):
        response = await self.client.post("/query", json=json_data)
        logger.debug("Response text is {}", response.text)
        return response.json()
