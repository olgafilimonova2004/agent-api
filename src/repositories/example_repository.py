from asyncpg.connection import Connection

from src.common.database.postgres import PostgresPool
from src.models.pydantic.example import ExampleData


class ExampleRepository:
    """
    ExampleTable:
    - id UUID
    - example_data varchar
    """

    def __init__(self, db: PostgresPool):
        self.db = db

    async def get_all(self, conn: Connection | None = None) -> list[ExampleData]:
        query = """
            SELECT * FROM "ExampleTable"
        """
        executor = conn if conn is not None else self.db
        rows = await executor.fetch(query)
        return [ExampleData.model_validate(dict(row)) for row in rows]

    async def get_all_external_conn(
        self,
        conn: Connection | None = None,
    ) -> list[ExampleData]:
        query = """
            SELECT * FROM "ExampleTable"
        """
        executor = conn if conn is not None else self.db
        rows = await executor.fetch(query)
        return [ExampleData.model_validate(dict(row)) for row in rows]
