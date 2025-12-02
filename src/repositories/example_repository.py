from src.common.database.postgres import PostgresPool


class ExampleRepository:
    
    def __init__(self, db: PostgresPool):
        self.db = db
    
    