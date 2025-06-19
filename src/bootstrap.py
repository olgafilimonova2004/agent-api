from src.application import Application
from src.clients.base_client import BaseClient
from src.common.database.postgres import db
from src.models.config import AppConfig
from src.repositories.example_repository import ExampleRepository
from src.routers.default import DefaultRouter
from src.services.example import ExampleService

def load_config() -> AppConfig:
    return AppConfig.create()

def bootstrap() -> Application:
    config = load_config()

    base_client = BaseClient('http://google.com')
    example_repo = ExampleRepository(db)
    example_service = ExampleService(base_client=base_client, example_repo=example_repo)
    default_router = DefaultRouter(example_service=example_service, base_prefix='/default', tags=['default'])

    return Application(config=config, default=default_router)