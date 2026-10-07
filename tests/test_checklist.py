import json
from pathlib import Path

import httpx
import pytest

from src.clients.llm import LLMService, LLMError
from src.models.config import LMConfig
from src.models.pydantic.checklist import UserChecklist
from src.services.checklist import ChecklistService

EXAMPLES = Path(__file__).resolve().parents[1] / "checklist_types_examples"


def checklist(name: str = "error") -> UserChecklist:
    return UserChecklist.model_validate_json((EXAMPLES / f"{name}.json").read_text())


def client_for(content: str, status: int = 200) -> LLMService:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        body = json.loads(request.content)
        assert body["model"] == "test-model"
        assert json.loads(body["messages"][1]["content"])["checklist_type"] in {
            "error",
            "improvement",
            "methodological",
            "technical",
        }
        return httpx.Response(
            status, json={"choices": [{"message": {"content": content}}]}
        )

    session = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return LLMService(LMConfig(base_url="http://lm/v1", model="test-model"), session)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["error", "improvement", "methodology", "technical"])
async def test_examples(name: str) -> None:
    data = checklist(name)
    first_key = data.answers[0].key
    service = ChecklistService(
        client_for(json.dumps(["contour", first_key, first_key]))
    )
    result = await service.validate(data)
    assert result == [first_key, "contour"]
    await service.client.close()


@pytest.mark.asyncio
async def test_empty_fields() -> None:
    data = checklist()
    data.answers[0].value = "  "
    data.answers[2].value = ""
    service = ChecklistService(client_for('["software_version"]'))
    assert await service.validate(data) == ["description"]
    await service.client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content", ["not json", '["unknown"]', '{"key": "description"}']
)
async def test_invalid_model_response(content: str) -> None:
    client = client_for(content)
    with pytest.raises(LMError):
        await client.validate(checklist())
    await client.close()


@pytest.mark.asyncio
async def test_lm_timeout() -> None:
    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    session = httpx.AsyncClient(transport=httpx.MockTransport(timeout))
    client = LLMService(LLMConfig(base_url="http://lm/v1"), session)
    with pytest.raises(LLMError):
        await client.validate(checklist())
    await client.close()


@pytest.mark.asyncio
async def test_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LM_BASE_URL", "http://lm/v1")
    monkeypatch.setattr(LLMService, "validate", fake_validate)
    from src.entrypoint.main import app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as api:
        for name in ("error", "improvement", "methodology", "technical"):
            data = json.loads((EXAMPLES / f"{name}.json").read_text())
            response = await api.post("/api/v1/checklists/validate", json=data)
            assert response.status_code == 200
            assert response.json() == {
                "invalid_fields": [data["answers"][0]["key"]],
                "search": None,
            }
        assert (await api.get("/api/v1/health")).json() == {"status": "ok"}


async def fake_validate(self: LLMService, data: UserChecklist) -> list[str]:
    return [data.answers[0].key]


@pytest.mark.asyncio
async def test_api_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LM_BASE_URL", "http://lm/v1")

    async def failed_validate(self: LLMService, data: UserChecklist) -> list[str]:
        raise LLMError("LM unavailable")

    monkeypatch.setattr(LLMService, "validate", failed_validate)
    from src.entrypoint.main import app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as api:
        data = json.loads((EXAMPLES / "error.json").read_text())
        assert (
            await api.post("/api/v1/checklists/validate", json=data)
        ).status_code == 502
        data["answers"][1]["key"] = data["answers"][0]["key"]
        assert (
            await api.post("/api/v1/checklists/validate", json=data)
        ).status_code == 422
