from pydantic import BaseModel, ConfigDict, Field


class VespaHitFields(BaseModel):
    model_config = ConfigDict(strict=True)
    page_id: str | None = None
    ticket_id: str | None = None
    text: str
    status: str | None = None


class VespaHit(BaseModel):
    model_config = ConfigDict(strict=True, allow_inf_nan=False)
    relevance: float
    fields: VespaHitFields


class VespaCoverage(BaseModel):
    full: bool = True


class VespaRoot(BaseModel):
    children: list[VespaHit] = Field(default_factory=list)
    errors: list[object] = Field(default_factory=list)
    coverage: VespaCoverage = Field(default_factory=VespaCoverage)


class VespaResponse(BaseModel):
    root: VespaRoot
    errors: list[object] = Field(default_factory=list)
