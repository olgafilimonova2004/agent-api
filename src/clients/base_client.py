from typing import Any, Self
from urllib.parse import urljoin

from httpx import AsyncClient, Response

from src.interfaces.client import IBaseClient


class BaseClient(IBaseClient):
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        session: AsyncClient | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ):
        self.base_url = base_url
        self.token = token
        self.session = session or AsyncClient()
        self.headers = headers
        self.params = params or {}

    @classmethod
    def create(cls, **kwargs: Any) -> Self:  # noqa: ANN206
        headers = kwargs.pop("headers", {})
        token = kwargs.pop("token", None)
        if token:
            headers.update({"X-Access-Token": token})
        base_url = kwargs.pop("base_url", None)
        timeout = kwargs.pop("timeout")
        session = AsyncClient(timeout=timeout) if timeout else AsyncClient()
        return cls(
            base_url=base_url,
            token=token,
            session=session,
            headers=headers,
        )

    async def patch(self, url: str, json: dict, **kwargs: Any) -> Response:
        return await self.session.patch(url=url, json=json, **kwargs)

    async def put(self, url: str, json: dict, **kwargs: Any) -> Response:
        return await self.session.patch(url=url, json=json, **kwargs)

    async def get(self, url: str, **kwargs: Any) -> Response:
        url = self.build_path(self.base_url + url)

        return await self.session.get(url=url, **kwargs)

    async def post(self, url: str, json: dict, **kwargs: Any) -> Response:
        return await self.session.post(url=url, json=json, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> Response:
        return await self.session.delete(url, **kwargs)

    async def close(self) -> None:
        await self.session.aclose()

    def build_path(self, path: str) -> str:
        """Build full URL from base path and relative path"""
        base = f"{self.base_url}/" if self.base_url[-1].isalpha() else self.base_url

        base = self.base_url if self.base_url.endswith("/") else f"{self.base_url}/"
        path = path.removeprefix("/")
        return urljoin(base, path)