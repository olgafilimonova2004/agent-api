from fastapi import APIRouter

from src.entrypoint.application import Application
from src.entrypoint.container import initialize_container
from src.models.config import AppConfig


def setup():
    container = initialize_container()
    config = container.get(AppConfig)
    routers = container.get(list[APIRouter])

    return Application(config=config, routers=routers, container=container)
