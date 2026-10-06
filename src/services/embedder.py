import math

import httpx

from src.common.errors import SearchError
from src.models.config import EmbedderConfig


class EmbedderService:
    def __init__(
        self, config: EmbedderConfig, session: httpx.AsyncClient | None = None
    ):
        self.config = config
        self.session = session or httpx.AsyncClient(timeout=config.timeout_seconds)

    async def embed(self, text: str) -> list[float]:
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = (
                f"Bearer {self.config.api_key.get_secret_value()}"
            )
        try:
            response = await self.session.post(
                f"{str(self.config.base_url).rstrip('/')}/embeddings",
                headers=headers,
                json={"model": self.config.model, "input": [self.config.prefix + text]},
            )
            response.raise_for_status()
            data = response.json()["data"]
            if not isinstance(data, list) or len(data) != 1:
                raise ValueError("Expected one embedding")
            if type(data[0]["index"]) is not int or data[0]["index"] != 0:
                raise ValueError("Invalid embedding index")
            vector = data[0]["embedding"]
            if not isinstance(vector, list) or len(vector) != 2048:
                raise ValueError("Expected a 2048-dimensional vector")
            if any(type(x) not in (int, float) or not math.isfinite(x) for x in vector):
                raise ValueError("Invalid vector values")
            return [float(x) for x in vector]
        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            IndexError,
            TypeError,
            OverflowError,
        ) as exc:
            raise SearchError(
                "Embedder request failed or returned an invalid vector"
            ) from exc

    async def close(self) -> None:
        await self.session.aclose()
