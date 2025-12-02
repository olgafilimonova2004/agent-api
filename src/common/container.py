from dishka import Scope, Container, Provider, provide, make_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.interfaces.router import BaseRouter
from src.models.config import AppConfig
from src.clients.base_client import BaseClient
from src.common.database.postgres import PostgresPool
from src.repositories.example_repository import ExampleRepository
from src.services.example import ExampleService
from src.routers.example import ExampleRouter


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> AppConfig:
        return AppConfig.initialize()


class ClientProvider(Provider):
    @provide(scope=Scope.APP)
    def get_base_client(self) -> BaseClient:
        return BaseClient(base_url="yandex.ru")


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_postgres(self, config: AppConfig) -> PostgresPool:
        return PostgresPool(config=config.postgres_config)


class RepositoryProvider(Provider):
    @provide(scope=Scope.APP)
    def get_example_repo(self, db: PostgresPool) -> ExampleRepository:
        return ExampleRepository(db=db)


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_example_service(
        self, client: BaseClient, repo: ExampleRepository
    ) -> ExampleService:
        return ExampleService(client=client, repo=repo)


class RouterProvider(Provider):
    @provide(scope=Scope.APP)
    def get_example_router(self, service: ExampleService) -> ExampleRouter:
        return ExampleRouter(example_service=service)

    @provide(scope=Scope.APP)
    def get_all_routers(self, example_router: ExampleRouter) -> list[BaseRouter]:
        return [example_router]


def initialize_container() -> Container:
    return make_container(
        ConfigProvider(), ClientProvider(), DatabaseProvider(), RepositoryProvider(), ServiceProvider(), RouterProvider()
    )


def setup_di(container: Container, app: FastAPI):
    return setup_dishka(container=container, app=app)
