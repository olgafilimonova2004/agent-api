from typing import Any

from src.clients.base_client import BaseClient
from src.repositories.example_repository import ExampleRepository


class ExampleService:
    def __init__(self, base_client: BaseClient, example_repo: ExampleRepository):
        self.base_client = base_client
        self.example_repo = example_repo

    async def example_method(self) -> Any:
        return await self.base_client.get("http://0.0.0.0:8000/ping")
