from uuid import UUID

from pydantic import BaseModel, Field


class ExampleData(BaseModel):
    "Pydantic модель примера данных"

    id: UUID = Field(..., description="ID примера данных")
    example_data: str = Field(..., description="Пример данных")
