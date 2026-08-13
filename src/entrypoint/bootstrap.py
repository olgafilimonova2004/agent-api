from src.entrypoint.application import Application
from src.entrypoint.container import initialize_container
from src.interfaces.router import IBaseRouter
from src.models.config import AppConfig


def setup():
    container = initialize_container()
    config = container.get(AppConfig)
    routers = container.get(list[IBaseRouter])

    return Application(config=config, routers=routers, container=container)
