from src.application import Application

from src.models.config import AppConfig
from src.interfaces.router import BaseRouter
from src.common.container import initialize_container



def setup():
    container = initialize_container()
    config = container.get(AppConfig)
    routers = container.get(list[BaseRouter])

    return Application(config=config, routers=routers, container=container)