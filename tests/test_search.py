import json
from pathlib import Path
from unittest.mock import AsyncMock, call

import httpx
import pytest
from dishka import make_container
from fastapi import APIRouter

from src.clients.llm import LLMService, LLMError
from src.common.errors import SearchError
from src.entrypoint.application import Application
from src.entrypoint.container import AppProvider
from src.models.config import AppConfig, EmbedderConfig, SearchConfig, VespaConfig
from src.models.pydantic.checklist import UserChecklist
from src.models.pydantic.confluence import ConfluenceRawRequest
from src.models.pydantic.search import JiraCandidate, SearchCandidate
from src.services.checklist import ChecklistService
from src.services.checklist_search import ChecklistSearchService
from src.services.confluence import ConfluenceService
from src.services.embedder import EmbedderService
from src.services.jira import JiraService
from src.services.search_query import SearchQueryBuilder
from src.services.vespa import VespaService

EXAMPLES = Path(__file__).resolve().parents[1] / "checklist_types_examples"


def payload(name="error"):
    return json.loads((EXAMPLES / f"{name}.json").read_text())


def services(confluence=None, jira=None):
    embedder = AsyncMock()
    embedder.embed.return_value = [0.1] * 2048
    vespa = AsyncMock()
    vespa.search_confluence.return_value = confluence
    vespa.search_jira.return_value = jira
    builder = SearchQueryBuilder()
    config = SearchConfig()
    jira_service = JiraService(embedder, vespa, builder, config)
    return (
        ConfluenceService(embedder, vespa, builder, jira_service, config),
        embedder,
        vespa,
    )


@pytest.mark.parametrize(
    "name,keys",
    [
        ("error", ["description"]),
        ("technical", ["description"]),
        ("methodology", ["question"]),
        ("improvement", ["summary", "proposal"]),
    ],
)
def test_prompts(name, keys):
    data = payload(name)
    request = ConfluenceRawRequest.model_validate(data)
    prompt = SearchQueryBuilder().construct(request)
    assert prompt.startswith(
        'Оператор отправил следующий вопрос о системе ПК РКМ "АРСЕНАЛ":'
    )
    context, content = prompt.split("Содержание вопроса:\n")
    for answer in data["answers"]:
        assert prompt.count(answer["value"]) >= 1
        if answer["key"] in keys:
            assert answer["value"] in content
            assert answer["value"] not in context
    assert data["user"]["phone"] not in prompt
    assert data["incident_id"] not in prompt
    request.answers.append(
        request.answers[-1].model_copy(
            update={"key": "empty", "title": "OMIT", "value": " "}
        )
    )
    assert "OMIT" not in SearchQueryBuilder().construct(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "score,expected",
    [(0.9, "confluence"), (0.8, "confluence"), (0.79, "jira"), (None, "jira")],
)
async def test_confluence_to_jira_branch(score, expected):
    candidate = (
        None if score is None else SearchCandidate(id="123", text="answer", score=score)
    )
    jira = JiraCandidate(id="RKMI-1", text="ticket", score=0.8, status="Open")
    service, embedder, vespa = services(candidate, jira)
    request = ConfluenceRawRequest.model_validate(payload())
    request.clarification = "Ошибка возникает при сохранении"
    confluence_vector, jira_vector = [0.1] * 2048, [0.2] * 2048
    embedder.embed.side_effect = [confluence_vector, jira_vector]
    result = await service.search(request)
    assert result.matched_source == expected
    confluence_query = embedder.embed.await_args_list[0].args[0]
    assert confluence_query.startswith("Оператор отправил следующий вопрос")
    assert request.clarification in confluence_query
    vespa.search_confluence.assert_awaited_once_with(
        confluence_vector, confluence_query
    )
    if expected == "jira":
        assert result.confluence is None
        assert result.jira == jira
        assert embedder.embed.await_count == 2
        jira_query = embedder.embed.await_args_list[1].args[0]
        assert jira_query.startswith("Найди описание похожего запроса/проблемы")
        assert request.clarification in jira_query
        assert "Найди подходящий ответ" not in jira_query
        vespa.search_jira.assert_awaited_once_with(jira_vector, jira_query)
    else:
        assert result.confluence == candidate
        assert result.jira is None
        embedder.embed.assert_awaited_once()
        vespa.search_jira.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("score", [None, 0.79])
async def test_direct_jira_no_match(score):
    jira = (
        None
        if score is None
        else JiraCandidate(id="1", text="ticket", score=score, status="Open")
    )
    service, embedder, vespa = services(jira=jira)
    result = await service.jira.search(ConfluenceRawRequest.model_validate(payload()))
    assert result.matched_source is None
    assert result.jira == jira
    vespa.search_confluence.assert_not_awaited()
    embedder.embed.assert_awaited_once()


@pytest.mark.asyncio
async def test_validation_gates_search():
    confluence, embedder, _ = services()
    lm = AsyncMock()
    lm.validate.return_value = []
    service = ChecklistSearchService(ChecklistService(lm), confluence)
    data = UserChecklist.model_validate(payload())
    data.answers[1].value = " "
    result = await service.validate(data)
    assert result.invalid_fields == ["contour"]
    embedder.embed.assert_not_awaited()
    data.answers[1].value = "ОПК"
    result = await service.validate(data)
    assert result.invalid_fields == []
    assert result.search is not None
    assert embedder.embed.await_count == 2


@pytest.mark.asyncio
async def test_embedder_contract():
    def handler(request):
        assert request.url.path == "/v1/embeddings"
        assert request.headers["authorization"] == "Bearer secret"
        assert json.loads(request.content) == {
            "model": "model",
            "input": ["prefix: question"],
        }
        return httpx.Response(
            200, json={"data": [{"index": 0, "embedding": [0.1] * 2048}]}
        )

    session = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = EmbedderService(
        EmbedderConfig(
            base_url="http://embed/v1",
            model="model",
            api_key="secret",
            prefix="prefix: ",
        ),
        session,
    )
    assert await client.embed("question") == [0.1] * 2048
    await client.close()
    assert session.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {},
        {"data": []},
        {"data": [{"index": 1, "embedding": [0.1] * 2048}]},
        {"data": [{"index": 0, "embedding": [0.1]}]},
        {"data": [{"index": 0, "embedding": [True] * 2048}]},
        {"data": [{"index": 0, "embedding": ["1"] * 2048}]},
        {"data": [{"index": 0, "embedding": [0.1] * 2048}] * 2},
    ],
)
async def test_invalid_embeddings(data):
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json=data))
    ) as session:
        with pytest.raises(SearchError):
            await EmbedderService(EmbedderConfig(), session).embed("question")


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["confluence", "jira"])
async def test_vespa_contract(source):
    def handler(request):
        body = json.loads(request.content)
        assert request.url.path == "/search/"
        assert body["hits"] == 1
        assert body["ranking"] == "weighted"
        assert body["query"] == "question"
        assert "rank(" in body["yql"]
        assert "userInput(@query)" in body["yql"]
        assert body["input.query(q_embedding)"] == [0.1] * 2048
        schema = "confluence_page" if source == "confluence" else "incident"
        assert f"from {schema} where" in body["yql"]
        assert "nearestNeighbor(embedding,q_embedding)" in body["yql"]
        fields = (
            {"text": "answer", "page_id": "123"}
            if source == "confluence"
            else {"text": "answer", "ticket_id": "RKMI-1", "status": "Open"}
        )
        return httpx.Response(
            200, json={"root": {"children": [{"relevance": 0.8, "fields": fields}]}}
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as session:
        client = VespaService(VespaConfig(), session)
        result = await (
            client.search_confluence([0.1] * 2048, "question")
            if source == "confluence"
            else client.search_jira([0.1] * 2048, "question")
        )
        assert result.text == "answer"
        assert result.score == 0.8


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {},
        {"root": {"errors": [{"message": "bad query"}]}},
        {"root": {"coverage": {"full": False}}},
        {"root": {"children": [{"relevance": 0.9, "fields": {"text": "missing id"}}]}},
    ],
)
async def test_invalid_vespa(data):
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json=data))
    ) as session:
        with pytest.raises(SearchError):
            await VespaService(VespaConfig(), session).search_confluence(
                [0.1] * 2048, "question"
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["embedder", "vespa"])
@pytest.mark.parametrize("failure", ["timeout", "http", "json"])
async def test_dependency_failures(kind, failure):
    def handler(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("timeout", request=request)
        return httpx.Response(503 if failure == "http" else 200, text="invalid")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as session:
        with pytest.raises(SearchError):
            if kind == "embedder":
                await EmbedderService(EmbedderConfig(), session).embed("question")
            else:
                await VespaService(VespaConfig(), session).search_jira(
                    [0.1] * 2048, "question"
                )


@pytest.mark.asyncio
async def test_confluence_failure_does_not_start_jira():
    service, _, vespa = services()
    vespa.search_confluence.side_effect = SearchError("unavailable")
    with pytest.raises(SearchError):
        await service.search(ConfluenceRawRequest.model_validate(payload()))
    vespa.search_jira.assert_not_awaited()


@pytest.mark.asyncio
async def test_api_and_cleanup(monkeypatch):
    monkeypatch.setenv("LM_BASE_URL", "http://lm/v1")
    monkeypatch.setattr(LLMService, "validate", AsyncMock(return_value=[]))
    monkeypatch.setattr(EmbedderService, "embed", AsyncMock(return_value=[0.1] * 2048))
    monkeypatch.setattr(VespaService, "search_confluence", AsyncMock(return_value=None))
    monkeypatch.setattr(VespaService, "search_jira", AsyncMock(return_value=None))
    container = make_container(AppProvider())
    app = Application(
        container.get(AppConfig), container.get(list[APIRouter]), container
    ).start_app()
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as api,
    ):
        for endpoint in ("checklists/validate", "confluence/search", "jira/search"):
            response = await api.post(f"/api/v1/{endpoint}", json=payload())
            assert response.status_code == 200
            result = response.json()
            if endpoint == "checklists/validate":
                assert result["invalid_fields"] == []
                result = result["search"]
            assert result == {"confluence": None, "jira": None, "matched_source": None}
        for endpoint in ("confluence/search", "jira/search"):
            data = payload()
            data["answers"][0]["value"] = " "
            assert (await api.post(f"/api/v1/{endpoint}", json=data)).status_code == 422
            data = payload()
            data["answers"].append(data["answers"][0])
            assert (await api.post(f"/api/v1/{endpoint}", json=data)).status_code == 422
        monkeypatch.setattr(
            EmbedderService, "embed", AsyncMock(side_effect=SearchError("unavailable"))
        )
        for endpoint in ("checklists/validate", "confluence/search", "jira/search"):
            assert (
                await api.post(f"/api/v1/{endpoint}", json=payload())
            ).status_code == 502
    for cls in (LLMService, EmbedderService, VespaService):
        assert container.get(cls).session.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
async def test_nonfinite_embedding(value):
    body = '{"data":[{"index":0,"embedding":[' + ",".join([value] * 2048) + "]}]}"
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    ) as session:
        with pytest.raises(SearchError):
            await EmbedderService(EmbedderConfig(), session).embed("question")


@pytest.mark.asyncio
async def test_missing_question_blocks_search():
    confluence, embedder, _ = services()
    lm = AsyncMock()
    lm.validate.return_value = []
    service = ChecklistSearchService(ChecklistService(lm), confluence)
    data = UserChecklist.model_validate(payload())
    data.answers = data.answers[1:]
    result = await service.validate(data)
    assert result.invalid_fields == ["description"]
    assert result.search is None
    embedder.embed.assert_not_awaited()


@pytest.mark.parametrize("name", ["error", "technical", "methodology", "improvement"])
@pytest.mark.parametrize(
    "clarification", [None, "", "  ", "  Первый ответ\nВторое уточнение  "]
)
def test_clarification_prompts(name, clarification):
    data = payload(name)
    data["clarification"] = clarification
    request = ConfluenceRawRequest.model_validate(data)
    builder = SearchQueryBuilder()
    for prompt in (builder.construct(request), builder.construct_jira(request)):
        if clarification and clarification.strip():
            assert prompt.count("Уточнения пользователя:") == 1
            assert prompt.count(clarification.strip()) == 1
        else:
            assert "Уточнения пользователя:" not in prompt
        for answer in data["answers"]:
            assert answer["value"] in prompt
    assert "clarification" not in UserChecklist.model_validate(data).model_dump()


@pytest.mark.asyncio
async def test_multiturn_search_is_stateless():
    candidate = SearchCandidate(id="123", text="answer", score=0.9)
    service, embedder, vespa = services(confluence=candidate)
    request = ConfluenceRawRequest.model_validate(payload())
    queries = []
    for clarification in (None, "При сохранении", "При сохранении\nТолько в ОПК", None):
        request.clarification = clarification
        await service.search(request)
        queries.append(embedder.embed.await_args.args[0])
    assert queries[0] == queries[3]
    assert "При сохранении" not in queries[0]
    assert queries[1].count("При сохранении") == 1
    assert queries[2].count("При сохранении\nТолько в ОПК") == 1
    assert vespa.search_confluence.await_args_list == [
        call(embedder.embed.return_value, query) for query in queries
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("score,expected", [(0.79, None), (0.8, "jira"), (1.5, "jira")])
async def test_direct_jira_threshold_and_query(score, expected):
    candidate = JiraCandidate(id="RKMI-1", text="ticket", status="Open", score=score)
    service, embedder, vespa = services(jira=candidate)
    request = ConfluenceRawRequest.model_validate(payload())
    request.clarification = "При сохранении"
    result = await service.jira.search(request)
    assert result.matched_source == expected
    assert result.confluence is None
    embedder.embed.assert_awaited_once()
    query = embedder.embed.await_args.args[0]
    assert query.startswith("Найди описание похожего запроса/проблемы")
    assert request.clarification in query
    vespa.search_jira.assert_awaited_once_with(embedder.embed.return_value, query)
    vespa.search_confluence.assert_not_awaited()


def test_weighted_threshold_can_exceed_one():
    assert SearchConfig(confluence_threshold=2, jira_threshold=3).jira_threshold == 3
