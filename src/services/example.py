from src.clients.base_client import BaseClient
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

    async def get_all(self) -> list[ExampleData]:
        return await self.repo.get_all()
