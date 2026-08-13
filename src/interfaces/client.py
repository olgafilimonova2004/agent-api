from collections.abc import Mapping
from types import TracebackType
from typing import Any, Protocol, Self, runtime_checkable

from httpx import AsyncClient, Response


@runtime_checkable
class IBaseClient(Protocol):
    base_url: str
    token: str | None
    _session: AsyncClient | None
    headers: dict[str, str] | None
    params: dict[str, Any] | None

    @property
    def session(self):
        if self.session is None:
            raise RuntimeError("Client Session is closed")
        return self.session

    @classmethod
    def create(cls, **kwargs: Any) -> "IBaseClient": ...

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response: ...

    async def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response: ...

    async def put(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response: ...

    async def patch(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response: ...

    async def delete(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response: ...

    def build_path(self, path: str) -> str: ...

    async def close(self) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
