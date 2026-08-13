from textwrap import dedent

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

    async def get_all(self) -> list[ExampleData]:
        query = dedent("""
            SELECT * FROM "ExampleTable"
        """)
        async with self.db.pool.acquire() as tx:
            rows = await tx._con.fetch(query)
        return [ExampleData.model_validate(dict(row)) for row in rows]

    async def get_all_external_conn(
        self,
        conn: Connection | None = None,
    ) -> list[ExampleData]:
        query = dedent("""
            SELECT * FROM "ExampleTable"
        """)
        if conn is not None:
            rows = await conn.fetch(query)
        else:
            async with self.db.pool.acquire() as tx:
                rows = await tx._con.fetch(query)
        return [ExampleData.model_validate(dict(row)) for row in rows]
