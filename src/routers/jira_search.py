from fastapi import APIRouter, HTTPException

from src.common.enums import RoutersMetainfo
from src.common.errors import SearchError
from src.models.pydantic.confluence import ConfluenceRawRequest
from src.models.pydantic.search import SearchResult
from src.services.jira import JiraService


class JiraSearchRouter:
    def __init__(self, service: JiraService):
        self.service = service
        tags = RoutersMetainfo.JIRA_TAGS.value
        prefix = RoutersMetainfo.DEFAULT_PREFIX.value
        self.api_router = APIRouter(prefix=prefix, tags=list(tags))
        self._register(self.api_router)

    def _register(self, router: APIRouter) -> None:
        @router.post("/jira/search", response_model=SearchResult)
        async def search(raw_request: ConfluenceRawRequest) -> SearchResult:
            try:
                return await self.service.search(raw_request)
            except SearchError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc
