from vespa.application import Vespa
from vespa.exceptions import VespaError
# TODO vespa client, accepts confluence or jira search requests and returns search results

class SearchClient:
    def __init__(self, vespa_url: str):
        self.vespa = Vespa(url=vespa_url)

    async def search(self, query: str) -> list[str]:
        try:
            response = self.vespa.query(body={"yql": query})
            if not response.is_successful():
                raise VespaError(f"Vespa query failed with status code {response.status_code}")
            return [hit["fields"]["title"] for hit in response.json["root"]["children"]]
        except Exception as e:
            raise VespaError(f"An error occurred while querying Vespa: {str(e)}") from e