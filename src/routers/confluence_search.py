from fastapi import APIRouter, HTTPException

from src.clients.lm_client import LMError
from src.common.enums import RoutersMetainfo
from src.interfaces.router import IBaseRouter
from src.services.confluence import ConfluenceService


class ConfluenceSearchRouter(IBaseRouter):
    def __init__(self, service: ConfluenceService):
        self.service = service
        self._tags = RoutersMetainfo.CONFLUENCE_TAGS.value
        self._base_prefix = RoutersMetainfo.DEFAULT_PREFIX.value

    def _register(self, router: APIRouter) -> None:
        @router.post("/confluence/search", response_model=list[str])
        async def search(raw_request: ConfluenceRawRequest) -> list[str]:
            try:
                return await self.service.search(raw_request)
            except LMError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc
