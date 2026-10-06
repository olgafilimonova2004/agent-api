from dishka import Container, Provider, Scope, make_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI

from src.clients.lm_client import LMClient
from src.models.config import AppConfig
from src.routers.checklist import ChecklistRouter
from src.routers.confluence_search import ConfluenceSearchRouter
from src.routers.health import HealthRouter
from src.routers.jira_search import JiraSearchRouter
from src.services.checklist import ChecklistService
from src.services.checklist_search import ChecklistSearchService
from src.services.confluence import ConfluenceService
from src.services.embedder import EmbedderService
from src.services.jira import JiraService
from src.services.search_query import SearchQueryBuilder
from src.services.vespa import VespaService


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
    def embedder(self, config: AppConfig) -> EmbedderService:
        return EmbedderService(config.embedder)

    @provide(scope=Scope.APP)
    def vespa(self, config: AppConfig) -> VespaService:
        return VespaService(config.vespa)

    @provide(scope=Scope.APP)
    def query_builder(self) -> SearchQueryBuilder:
        return SearchQueryBuilder()

    @provide(scope=Scope.APP)
    def jira(
        self,
        embedder: EmbedderService,
        vespa: VespaService,
        builder: SearchQueryBuilder,
        config: AppConfig,
    ) -> JiraService:
        return JiraService(embedder, vespa, builder, config.search)

    @provide(scope=Scope.APP)
    def confluence(
        self,
        embedder: EmbedderService,
        vespa: VespaService,
        builder: SearchQueryBuilder,
        jira: JiraService,
        config: AppConfig,
    ) -> ConfluenceService:
        return ConfluenceService(embedder, vespa, builder, jira, config.search)

    @provide(scope=Scope.APP)
    def checklist_search(
        self, validator: ChecklistService, confluence: ConfluenceService
    ) -> ChecklistSearchService:
        return ChecklistSearchService(validator, confluence)

    @provide(scope=Scope.APP)
    def routers(
        self,
        service: ChecklistSearchService,
        confluence: ConfluenceService,
        jira: JiraService,
    ) -> list[APIRouter]:
        return [
            ChecklistRouter(service).api_router,
            ConfluenceSearchRouter(confluence).api_router,
            JiraSearchRouter(jira).api_router,
            HealthRouter().api_router,
        ]


def initialize_container() -> Container:
    return make_container(AppProvider())


def setup_di(container: Container, app: FastAPI) -> None:
    setup_dishka(container=container, app=app)
