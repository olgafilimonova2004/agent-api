import httpx

from src.common.errors import SearchError
from src.models.config import VespaConfig
from src.models.pydantic.search import JiraCandidate, SearchCandidate, SearchSource
from src.models.pydantic.vespa import VespaHit, VespaResponse


class VespaService:
    def __init__(self, config: VespaConfig, session: httpx.AsyncClient | None = None):
        self.config = config
        self.session = session or httpx.AsyncClient(timeout=config.timeout_seconds)

    async def _search(
        self, vector: list[float], query: str, source: SearchSource
    ) -> VespaHit | None:
        schema = "confluence_page" if source == "confluence" else "incident"
        fields = (
            "page_id, text" if source == "confluence" else "ticket_id, text, status"
        )
        try:
            response = await self.session.post(
                f"{str(self.config.url).rstrip('/')}/search/",
                json={
                    "yql": f"select {fields} from {schema} where "
                    "rank({targetHits:1,approximate:false}nearestNeighbor(embedding,q_embedding), "
                    "userInput(@query))",
                    "hits": 1,
                    "ranking": "weighted",
                    "query": query,
                    "input.query(q_embedding)": vector,
                },
            )
            response.raise_for_status()
            result = VespaResponse.model_validate(response.json())
            if result.errors or result.root.errors or not result.root.coverage.full:
                raise ValueError("Vespa returned errors or partial coverage")
            if not result.root.children:
                return None
            return max(result.root.children, key=lambda hit: hit.relevance)
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise SearchError(
                "Vespa request failed or returned an invalid response"
            ) from exc

    async def search_confluence(
        self, vector: list[float], query: str
    ) -> SearchCandidate | None:
        hit = await self._search(vector, query, "confluence")
        if hit is None:
            return None
        if not hit.fields.page_id:
            raise SearchError("Vespa returned a Confluence hit without page_id")
        return SearchCandidate(
            id=hit.fields.page_id, text=hit.fields.text, score=hit.relevance
        )

    async def search_jira(
        self, vector: list[float], query: str
    ) -> JiraCandidate | None:
        hit = await self._search(vector, query, "jira")
        if hit is None:
            return None
        if not hit.fields.ticket_id or hit.fields.status is None:
            raise SearchError("Vespa returned a Jira hit without ticket_id or status")
        return JiraCandidate(
            id=hit.fields.ticket_id,
            text=hit.fields.text,
            score=hit.relevance,
            status=hit.fields.status,
        )

    async def close(self) -> None:
        await self.session.aclose()
