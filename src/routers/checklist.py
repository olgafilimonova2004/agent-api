from fastapi import APIRouter, HTTPException

from src.clients.llm import LLMError
from src.common.enums import RoutersMetainfo
from src.common.errors import SearchError
from src.models.pydantic.checklist import UserChecklist
from src.models.pydantic.search import ChecklistValidationResponse
from src.services.checklist_search import ChecklistSearchService


class ChecklistRouter:
    def __init__(self, service: ChecklistSearchService):
        self.service = service
        tags = RoutersMetainfo.CHECKLIST_TAGS.value
        prefix = RoutersMetainfo.DEFAULT_PREFIX.value
        self.api_router = APIRouter(prefix=prefix, tags=list(tags))
        self._register(self.api_router)

    def _register(self, router: APIRouter) -> None:
        @router.post("/checklists/validate", response_model=ChecklistValidationResponse)
        async def validate(checklist: UserChecklist) -> ChecklistValidationResponse:
            try:
                return await self.service.validate(checklist)
            except (LLMError, SearchError) as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc
