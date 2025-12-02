from typing import Any, Mapping, Self
from urllib.parse import urljoin

from httpx import AsyncClient, Response

from src.interfaces.client import IBaseClient


class BaseClient(IBaseClient):
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        session: AsyncClient | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.username = username
        self.password = password
        self.session = session or AsyncClient(timeout=30.0)
        self.headers = headers or {}
        self.params = params or {}

    @classmethod
    def create(cls, **kwargs: Any) -> Self:
        headers: dict[str, str] = kwargs.pop("headers", {}) or {}
        token = kwargs.pop("token", None)
        if token:
            headers["X-Access-Token"] = token
        base_url = kwargs.pop("base_url", "")
        timeout = kwargs.pop("timeout", 30.0)
        session = AsyncClient(timeout=timeout)
        return cls(
            base_url=base_url,
            token=token,
            session=session,
            headers=headers,
        )

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response:
        full_url = self.build_path(url)
        return await self.session.get(
            url=full_url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

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
    ) -> Response:
        full_url = self.build_path(url)
        return await self.session.post(
            url=full_url,
            json=json,
            data=data,
            content=content,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

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
    ) -> Response:
        full_url = self.build_path(url)
        return await self.session.put(
            url=full_url,
            json=json,
            data=data,
            content=content,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

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
    ) -> Response:
        full_url = self.build_path(url)
        return await self.session.patch(
            url=full_url,
            json=json,
            data=data,
            content=content,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def delete(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Response:
        full_url = self.build_path(url)
        return await self.session.delete(
            url=full_url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def build_path(self, path: str) -> str:
        base = f"{self.base_url}/"
        path = path.lstrip("/")
        return urljoin(base, path)

    async def close(self) -> None:
        if self.session:
            await self.session.aclose()

    async def __aenter__(self) -> "BaseClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
