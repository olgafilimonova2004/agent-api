from src.models.config import SearchConfig
from src.models.pydantic.confluence import ConfluenceRawRequest
from src.models.pydantic.search import SearchResult
from src.services.embedder import EmbedderService
from src.services.jira import JiraService
from src.services.search_query import SearchQueryBuilder
from src.services.vespa import VespaService


class ConfluenceService:
    def __init__(
        self,
        embedder: EmbedderService,
        vespa: VespaService,
        builder: SearchQueryBuilder,
        jira: JiraService,
        config: SearchConfig,
    ):
        self.embedder = embedder
        self.vespa = vespa
        self.builder = builder
        self.jira = jira
        self.config = config

    async def construct_search_query(self, raw_request: ConfluenceRawRequest) -> str:
        return self.builder.construct(raw_request)

    async def search(self, raw_request: ConfluenceRawRequest) -> SearchResult:
        query = await self.construct_search_query(raw_request)
        vector = await self.embedder.embed(query)
        candidate = await self.vespa.search_confluence(vector, query)
        if (
            candidate is not None
            and candidate.score >= self.config.confluence_threshold
        ):
            return SearchResult(confluence=candidate, matched_source="confluence")
        return await self.jira.search(raw_request)
