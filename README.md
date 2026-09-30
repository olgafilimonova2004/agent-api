# Checklist Validator

HTTP-сервис проверяет заполненный чеклист и возвращает ключи полей, которые нужно заполнить заново. Поддерживаются типы `error`, `improvement`, `methodological`, `technical` из `checklist_types_examples/`. Для оценки используется внешняя Qwen с OpenAI-совместимым API.

## Структура

- `src/models/pydantic/checklist.py` — входная Pydantic-модель чеклиста и полей.
- `src/models/config.py` — настройки Qwen из переменных окружения.
- `src/clients/qwen.py` — HTTP-запрос к `/v1/chat/completions` и проверка ответа модели.
- `src/services/checklist.py` — правила для обязательных и необязательных полей, объединение результата в порядке `answers`.
- `src/routers/checklist.py` — HTTP-маршрут проверки.
- `src/entrypoint/` — сборка FastAPI, зависимостей и закрытие HTTP-клиента.
- `checklist_types_examples/` — четыре примера входного JSON.

## Запуск

Требуются Python 3.12+ и uv. Скопируйте `.env.example` в `.env` и задайте `QWEN_BASE_URL` как адрес OpenAI-совместимого API с суффиксом `/v1`. `QWEN_MODEL` задаёт имя модели, `QWEN_API_KEY` необязателен, `QWEN_TIMEOUT_SECONDS` задаёт таймаут запроса. Затем запустите:

```bash
uv sync
uv run --env-file .env main.py
```

Для Docker скопируйте настройки в `.env.docker`, укажите доступный контейнеру адрес Qwen и выполните `docker compose up --build`.

## API

`POST /api/v1/checklists/validate` принимает полный JSON чеклиста. Ответ — массив ключей из `answers` в исходном порядке, например `["description", "proposal"]`. Пустое обязательное поле требует заполнения; пустое необязательное пропускается. Непустые значения проверяет модель по `key`, `title` и `value`. Ошибка схемы входа даёт HTTP 422, ошибка или некорректный ответ Qwen — HTTP 502.

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
