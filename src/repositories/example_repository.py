from src.common.database.postgres import DatabaseSessionManager


class ExampleRepository:
    
    def __init__(self, conn: DatabaseSessionManager):
        self._session = conn
    
    