from dishka import Container, Provider, Scope, make_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.clients.lm_client import LMClient
from src.interfaces.router import IBaseRouter
from src.models.config import AppConfig
from src.routers.checklist import ChecklistRouter
from src.routers.health import HealthRouter
from src.services.checklist import ChecklistService


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def config(self) -> AppConfig:
        return AppConfig()

    @provide(scope=Scope.APP)
    def client(self, config: AppConfig) -> LMClient:
        return LMClient(config.lm)

    @provide(scope=Scope.APP)
    def service(self, client: LMClient) -> ChecklistService:
        return ChecklistService(client)

    @provide(scope=Scope.APP)
    def routers(self, service: ChecklistService) -> list[IBaseRouter]:
        return [ChecklistRouter(service), HealthRouter()]


def initialize_container() -> Container:
    return make_container(AppProvider())


def setup_di(container: Container, app: FastAPI) -> None:
    setup_dishka(container=container, app=app)
