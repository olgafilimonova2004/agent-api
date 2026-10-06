from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SearchSource = Literal["confluence", "jira"]


class SearchCandidate(BaseModel):
    model_config = ConfigDict(strict=True, allow_inf_nan=False)

    id: str
    text: str
    score: float


class JiraCandidate(SearchCandidate):
    status: str


class SearchResult(BaseModel):
    confluence: SearchCandidate | None = None
    jira: JiraCandidate | None = None
    matched_source: SearchSource | None = None


class ChecklistValidationResponse(BaseModel):
    invalid_fields: list[str] = Field(default_factory=list)
    search: SearchResult | None = None
