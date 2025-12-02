from abc import ABC, abstractmethod

from fastapi import APIRouter


class BaseRouter(ABC):
    tags: list[str] | None
    prefix: str | None

    @property
    @abstractmethod
    def router(self) -> APIRouter:
        raise NotImplementedError

    @abstractmethod
    def initialize(self, router: APIRouter) -> None:
        raise NotImplementedError
