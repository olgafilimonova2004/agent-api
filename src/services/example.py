from typing import Any

from src.clients.base_client import BaseClient
from src.repositories.example_repository import ExampleRepository


class ExampleService:
    def __init__(
        self,
        client: BaseClient,
        repo: ExampleRepository,
    ):
        self.client = client
        self.repo = repo

    async def some_method(self) -> None:
        pass
