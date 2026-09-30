from fastapi import APIRouter, HTTPException

from src.clients.lm_client import LMError
from src.common.enums import RoutersMetainfo
from src.interfaces.router import IBaseRouter
from src.models.pydantic.checklist import UserChecklist
from src.services.checklist import ChecklistService


class ChecklistRouter(IBaseRouter):
    def __init__(self, service: ChecklistService):
        self.service = service
        self._tags = RoutersMetainfo.CHECKLIST_TAGS.value
        self._base_prefix = RoutersMetainfo.DEFAULT_PREFIX.value

    def _register(self, router: APIRouter) -> None:
        @router.post("/checklists/validate", response_model=list[str])
        async def validate(checklist: UserChecklist) -> list[str]:
            try:
                return await self.service.validate(checklist)
            except LMError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc
