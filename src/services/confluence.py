from src.clients.search_client import SearchClient
from src.models.pydantic.confluence import ConfluenceRawRequest


class ConfluenceService:
    def __init__(self, client: SearchClient):
        self.client = client

    async def construct_search_query(self, raw_request: ConfluenceRawRequest) -> str:
        #TODO: implement logic to construct search query from raw_request
        pass
        
    async def search(self, raw_request: ConfluenceRawRequest) -> list[str]:
        request = await self.construct_search_query(raw_request)
        return await self.client.search(request)

