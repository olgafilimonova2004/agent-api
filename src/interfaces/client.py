from typing import Any, Mapping, Protocol, runtime_checkable

from httpx import AsyncClient, Response


@runtime_checkable
class IBaseClient(Protocol):
    base_url: str
    token: str | None
    session: AsyncClient | None
    headers: dict[str, str] | None
    params: dict[str, Any] | None

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

    async def __aenter__(self) -> "IBaseClient": ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
