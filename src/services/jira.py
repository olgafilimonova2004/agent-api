from src.models.config import SearchConfig
from src.models.pydantic.confluence import ConfluenceRawRequest
from src.models.pydantic.search import SearchResult
from src.services.embedder import EmbedderService
from src.services.search_query import SearchQueryBuilder
from src.services.vespa import VespaService


class JiraService:
    def __init__(
        self,
        embedder: EmbedderService,
        vespa: VespaService,
        builder: SearchQueryBuilder,
        config: SearchConfig,
    ):
        self.embedder = embedder
        self.vespa = vespa
        self.builder = builder
        self.config = config

    async def search(self, request: ConfluenceRawRequest) -> SearchResult:
        query = self.builder.construct_jira(request)
        vector = await self.embedder.embed(query)
        candidate = await self.vespa.search_jira(vector, query)
        matched = (
            candidate is not None and candidate.score >= self.config.jira_threshold
        )
        return SearchResult(jira=candidate, matched_source="jira" if matched else None)
