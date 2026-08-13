from abc import ABC, abstractmethod

from fastapi import APIRouter


class IBaseRouter(ABC):
    _tags: tuple[str] | None
    _base_prefix: str

    @property
    def tags(self) -> tuple[str] | None:
        return self._tags

    @property
    def base_prefix(self) -> str:
        return self._base_prefix

    @property
    def api_router(self) -> APIRouter:
        server = APIRouter()
        self._register(server)
        return server

    @abstractmethod
    def _register(self, router: APIRouter) -> None:
        raise NotImplementedError
