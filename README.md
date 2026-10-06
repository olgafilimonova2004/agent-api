# Checklist Validator

HTTP-сервис проверяет заполненный чеклист и ищет подходящие документы Confluence или похожие инциденты Jira, если проверка прошла. Поддерживаются типы `error`, `improvement`, `methodological`, `technical` из `checklist_types_examples/`. Для оценки используется внешняя языковая модель с OpenAI-совместимым API.

## Структура

- `src/models/pydantic/checklist.py` — входная Pydantic-модель чеклиста и полей.
- `src/models/config.py` — настройки языковой модели из переменных окружения.
- `src/clients/lm_client.py` — HTTP-запрос к `/v1/chat/completions` и проверка ответа модели.
- `src/services/checklist.py` — правила для обязательных и необязательных полей, объединение результата в порядке `answers`.
- `src/routers/checklist.py` — HTTP-маршрут проверки.
- `src/entrypoint/` — сборка FastAPI, зависимостей и закрытие HTTP-клиента.
- `checklist_types_examples/` — четыре примера входного JSON.

## Запуск

Требуются Python 3.12+ и uv. Скопируйте `.env.example` в `.env` и задайте `LM_BASE_URL` как адрес OpenAI-совместимого API с суффиксом `/v1`. `LM_MODEL` задаёт имя модели, `LM_API_KEY` необязателен, `LM_TIMEOUT_SECONDS` задаёт таймаут запроса. Затем запустите:

```bash
uv sync
uv run --env-file .env main.py
```

Для Docker скопируйте настройки в `.env.docker`, укажите доступный контейнеру адрес языковой модели и выполните `docker compose up --build`.

## API

`POST /api/v1/checklists/validate` принимает полный JSON чеклиста. Ответ — объект `{"invalid_fields": ["description", "proposal"], "search": null}`. Это изменение прежнего контракта, возвращавшего массив. При успешной проверке `invalid_fields` пуст, а `search` содержит результат поиска. Пустое обязательное поле требует заполнения; пустое необязательное пропускается. Непустые значения проверяет модель по `key`, `title` и `value`. Ошибка схемы входа даёт HTTP 422, ошибка или некорректный ответ языковой модели — HTTP 502.

```bash
curl -X POST http://localhost:8000/api/v1/checklists/validate \
  -H 'Content-Type: application/json' \
  --data-binary @checklist_types_examples/error.json
```

Замените `error.json` на `improvement.json`, `methodology.json` или `technical.json` для остальных типов. `GET /api/v1/ping` возвращает `"pong"`; `GET /api/v1/health` возвращает `{"status":"ok"}`. Swagger UI доступен по `/docs`.

## Проверки

```bash
uv run pytest
uvx ruff check .
uvx ruff format --check .
uvx ty check
```

## Поиск Confluence и Jira

`POST /api/v1/confluence/search` и `POST /api/v1/jira/search` принимают поля
`checklist_type`, `checklist_title`, `component`, `answers` из примеров чеклистов.
Можно передать полный чеклист: остальные поля игнорируются. Ключи ответов должны
быть уникальными. Обязателен непустой `description` для error/technical,
`question` для methodological, оба `summary` и `proposal` для improvement.
Ошибки входа возвращают HTTP 422.

```bash
curl -X POST http://localhost:8000/api/v1/confluence/search \
  -H 'Content-Type: application/json' \
  --data-binary @checklist_types_examples/error.json
curl -X POST http://localhost:8000/api/v1/jira/search \
  -H 'Content-Type: application/json' \
  --data-binary @checklist_types_examples/error.json
```

Поиск Confluence возвращает один ближайший документ. Если его нет или оценка
меньше `SEARCH_CONFLUENCE_THRESHOLD`, выполняется поиск одного инцидента Jira
с отдельным запросом и новым вектором. Прямой вызов Jira пропускает Confluence. Оценка, равная порогу,
считается подходящей. Оба порога по умолчанию равны 0.8 и требуют калибровки на
реальных запросах; это оценки Vespa weighted (0.5 × closeness + 0.5 × BM25), а не вероятности.
Оценки могут превышать 1; верхняя граница порогов не ограничена.

Пример ответа поиска:

```json
{
  "confluence": null,
  "jira": {"id": "RKMI-42", "text": "Описание инцидента", "score": 0.9, "status": "Open"},
  "matched_source": "jira"
}
```

При переходе в Jira кандидат Confluence не сохраняется: `confluence` равен `null`.
Отсутствующие кандидаты также равны `null`. Кандидат Jira ниже порога сохраняется, но `matched_source` указывает только источник подходящего результата; если его нет,
значение равно `null`. При успешной валидации этот объект находится в поле `search`.
Ошибки embedder/Vespa, некорректные ответы и неполное покрытие Vespa дают HTTP 502,
а не результат «ничего не найдено». Создание/связывание тикетов и уведомления
выполняет вызывающий сервис. Для поиска после нажатия кнопки вызывайте Jira endpoint.

## Настройки поиска

Настройки считываются из окружения; при локальном запуске используйте
`uv run --env-file .env main.py`, в Docker — `.env.docker`.

| Переменная | Назначение / значение по умолчанию |
| --- | --- |
| `EMBEDDER_BASE_URL` | Адрес существующего контейнера embedder с `/v1`; `http://embedder:8000/v1` |
| `EMBEDDER_MODEL` | Задайте ту же модель, что в `INCIDENT_EMBEDDER_MODEL` индексатора |
| `EMBEDDER_API_KEY` | Необязательный Bearer-токен |
| `EMBEDDER_PREFIX` | Тот же префикс, что в `INCIDENT_EMBEDDER_PREFIX`; по умолчанию пуст |
| `EMBEDDER_TIMEOUT_SECONDS` | 120 |
| `VESPA_URL` | `http://vespa:8080` |
| `VESPA_TIMEOUT_SECONDS` | 30 |
| `SEARCH_CONFLUENCE_THRESHOLD` | 0.8, неотрицательное число |
| `SEARCH_JIRA_THRESHOLD` | 0.8, неотрицательное число |

Используется `/embeddings` с OpenAI-совместимым протоколом. Размерность фиксирована
в 2048 согласно существующим схемам Vespa; модель должна совпадать с индексатором.
Имена хостов в шаблоне замените адресами, доступными из API-контейнера, либо
подключите контейнеры к общей Docker-сети. Новый контейнер модели не создаётся.

Vespa запрашивается асинхронно через HTTP `/search/`, с `weighted` ranking и точным
`nearestNeighbor` (`approximate:false`, `hits:1`). Точный поиск соответствует
примеру индексатора; для больших индексов оцените задержку перед эксплуатацией.
Текст передаётся параметром `query` через `userInput(@query)` для BM25;
`rank(nearestNeighbor(...), userInput(@query))` использует векторный отбор и
лексические признаки для оценки найденного кандидата.
В запрос передаются поля чеклиста и уточнения, без идентификаторов и контактов пользователя.

## Уточнения в диалоге

Поисковые endpoints принимают необязательное поле `clarification: string | null`.
При каждом ходе клиент передаёт исходный checklist и все накопленные уточнения
одной строкой. API не хранит историю. Пустые уточнения пропускаются.
`UserChecklist` на стадии валидации не содержит это поле.

Например, первый запрос выполняется с `checklist_types_examples/error.json`,
а повторный запрос — с теми же полями и дополнительным полем:

```json
{
  "checklist_type": "error",
  "checklist_title": "Ошибка",
  "component": "Функционал",
  "answers": [
    {"key": "description", "title": "Описание ошибки", "is_required": true,
     "value": "Не удаётся сохранить документ"}
  ],
  "clarification": "Ошибка возникает при сохранении.\nПовторяется только в контуре ОПК."
}
```

Отправьте этот JSON в `POST /api/v1/confluence/search` для повторного поиска
решения или в `POST /api/v1/jira/search` после нажатия кнопки поиска похожей проблемы.
Confluence использует инструкцию «Найди подходящий ответ на запрос в базе знаний.»,
Jira — префикс «Найди описание похожего запроса/проблемы». Оба запроса включают
исходное содержание и блок «Уточнения пользователя:».

HTTP-вызовы поиска находятся в конкретных `EmbedderService` и `VespaService`
в `src/services/`; `ConfluenceService` и `JiraService` управляют последовательностью
поиска. Роутеры используют `APIRouter` без слоя interfaces.
