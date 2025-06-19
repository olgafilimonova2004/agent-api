from abc import ABC, abstractmethod

from fastapi import APIRouter


class BaseRouter(ABC):
    @property
    @abstractmethod
    def base_prefix(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def tags(self) -> list[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def api_router(self) -> APIRouter:
        raise NotImplementedError

    @abstractmethod
    def _register(self, router: APIRouter) -> None:
        raise NotImplementedError
