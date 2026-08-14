# API Base

> Пример основы для новых HTTP API-сервисов на FastAPI.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.137%2B-009688.svg)](https://fastapi.tiangolo.com/)

## Назначение

Репозиторий содержит минимальный рабочий каркас сервиса с разделением HTTP-слоя, бизнес-логики и доступа к данным. Его следует копировать и адаптировать под конкретный сервис, удаляя демонстрационные компоненты, которые не нужны проекту.

В примере уже настроены:

- FastAPI и Uvicorn;
- DI-контейнер Dishka;
- асинхронный пул PostgreSQL на AsyncPG;
- базовый HTTP-клиент на HTTPX;
- Pydantic Settings для конфигурации из окружения;
- повторные попытки подключения через Tenacity;
- преобразование основных ошибок AsyncPG в HTTP-ошибки;
- Ruff, ty и pre-commit hooks;
- сборка обычного и multi-stage/non-root Docker-образов.

Это слоистый шаблон, вдохновлённый Clean Architecture, а не полная реализация DDD: доменные сущности, агрегаты, bounded contexts и миграции в него намеренно не включены.

## Структура проекта

```text
api-base/
├── main.py                         # Локальная точка запуска
├── pyproject.toml                  # Метаданные, зависимости и console script
├── uv.lock                         # Зафиксированные версии зависимостей (полностью управляется uv, не human-readable)
├── Dockerfile                      # Основной образ
├── Dockerfile.multistage_nonroot   # Multi-stage образ с кастомным пользователем с uid по аргументу
├── docker-compose.yaml             # Приложение и PostgreSQL
└── src/
    ├── clients/
    │   └── base_client.py          # Асинхронный HTTP-клиент
    ├── common/
    │   ├── database/postgres.py    # Пул соединений PostgreSQL
    │   ├── decorators.py           # Retry policy, другие декораторы
    │   ├── enums.py                # Метаданные роутеров, другие определения Enum
    │   └── errors.py               # HTTP-ошибки и обработка ошибок БД или другие определения ошибок
    ├── entrypoint/
    │   ├── application.py          # FastAPI, middleware и lifespan
    │   ├── bootstrap.py            # Сборка приложения
    │   ├── container.py            # DI контейнер
    │   └── main.py                 # ASGI app и console script
    ├── interfaces/                 # Интерфейсы и абстракции
    ├── models/
    │   ├── config.py               # Конфигурация приложения
    │   └── pydantic/example.py     # Модели данных
    ├── repositories/               # Репозитории для работы с данными
    ├── routers/                    # FastAPI роутеры
    └── services/                   # Бизнес-логика
```

Поток зависимостей для демонстрационного endpoint:

```text
HTTP request -> ExampleRouter -> ExampleService -> ExampleRepository -> PostgreSQL
```

Объекты собираются в `src/entrypoint/container.py`. Подключение к PostgreSQL создаётся при старте приложения и закрывается в его lifespan, поэтому без доступной БД сервис не запустится.

## Требования

- Python 3.12+ (можно понижать версию до тех пор, пока uv lock сможет разрешать зависимости)
- [uv](https://github.com/astral-sh/uv)
- PostgreSQL (для работы с БД)

## Быстрый старт

### 1. Установка зависимостей

```bash
uv sync
```

### 2. Переменные окружения

Скопируйте `.env.example` в `.env` (или в `.env.docker` для docker mode) в корне проекта и настройте необходимые переменные

### 3. Запуск PostgreSQL

После создания `.env` можно запустить только БД из Compose:

```bash
docker compose up -d db
```

Либо используйте уже доступный экземпляр PostgreSQL и укажите его адрес в `POSTGRES_DSN`.

### 4. Запуск приложения

```bash
uv run --env-file .env main.py
```

Сервис слушает `http://localhost:8000`. Интерактивная документация доступна по адресам:

- Swagger UI: `http://localhost:8000/docs`;
- ReDoc: `http://localhost:8000/redoc`;
- OpenAPI: `http://localhost:8000/openapi.json`.

## Запуск в Docker

Для контейнера приложения создайте `.env.docker`. Имя хоста PostgreSQL должно совпадать с именем Compose-сервиса `db`:

```dotenv
POSTGRES_DSN=postgresql://local:local@db:5432/local
POSTGRES_MIN_SIZE=1
POSTGRES_MAX_SIZE=10
POSTGRES_MAX_CONN_ATTEMPT=5
```

Затем выполните:

```bash
docker compose up --build -d
```

Для сборки отдельного образа:

```bash
docker build -t api-base .
docker run --rm -p 8000:8000 --env-file .env.docker api-base
```

При отдельном запуске контейнера значение `POSTGRES_DSN` должно указывать на БД, доступную из его Docker-сети; Compose-имя `db` работает только внутри сети Compose.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/ping` | Liveness-проверка, возвращает `"pong"` |
| `GET` | `/api/v1/health` | Health-проверка, возвращает `{"status": "ok"}` |
| `GET` | `/api/v1/` | Демонстрационное получение записей из `ExampleTable` |

Health-маршруты становятся доступны только после успешного старта приложения, включая создание пула БД.

Демонстрационный endpoint ожидает существующую таблицу PostgreSQL:

```sql
CREATE TABLE "ExampleTable" (
    id uuid PRIMARY KEY,
    example_data varchar NOT NULL
);
```

Миграции в шаблон не входят. Добавьте выбранный инструмент миграций в производном проекте либо удалите `ExampleRepository` и демонстрационный маршрут.

## Как адаптировать шаблон

1. Измените имя и описание пакета в `pyproject.toml`, а также console script `api-base`.
2. Синхронно переименуйте сервис и образ в Docker-конфигурации.
3. Определите конфигурацию сервиса в `src/models/config.py`.
4. Замените демонстрационные model, repository, service и router своими реализациями.
5. Зарегистрируйте новые зависимости и роутеры в `src/entrypoint/container.py`.
6. Обновите префиксы и теги в `src/common/enums.py`.
7. Настройте CORS в `src/entrypoint/application.py`: значение `*` предназначено только для основы и локальной разработки.
8. Добавьте миграции, тесты, наблюдаемость и CI/CD в соответствии с требованиями сервиса.
9. Пересоздайте lock-файл командой `uv lock` после изменения зависимостей.

## Разработка

### Окончания строк

На Windows настройте Git для единообразной работы с окончаниями строк:

```bash
git config core.autocrlf true
git config core.safecrlf true
```

Если такая политика нужна для всех репозиториев текущего пользователя, используйте глобальные настройки:

```bash
git config --global core.autocrlf true
git config --global core.safecrlf true
```

`core.autocrlf` преобразует LF в CRLF при checkout и возвращает LF при commit, а `core.safecrlf` запрещает потенциально необратимое преобразование окончаний строк. Без `--global` настройки действуют только в текущем репозитории; глобальный вариант стоит использовать лишь при одинаковой политике во всех проектах. Для Linux/macOS обычно используют `core.autocrlf input`.

### Python-пакеты

В каждой директории внутри `src/` обязателен пустой файл `__init__.py`. В VS Code их можно скрыть через создание/модификацию файла `.vscode/settings.json`:

```json
{
  "files.exclude": {
    "**/__init__.py": true
  }
}
```

При добавлении новых слоев, однако, файлы не создаются автоматически

### Проверки качества

Конфигурация pre-commit запускает:

- `ruff-check` с автоисправлением;
- `ruff-format`;
- `ty` для проверки типов;
- стандартные проверки текстовых и YAML-файлов;
- `detect-private-key` и `gitleaks`.

Установка Git hooks и ручной запуск всех проверок:

```bash
uvx pre-commit install
uvx pre-commit run --all-files
```

Отдельный запуск линтера, форматтера и проверки типов:

```bash
uvx ruff check .
uvx ruff format --check .
uvx ty check
```

### Тесты

`pytest` и `pytest-asyncio` доступны в окружении проекта, но готовых тестов в шаблоне пока нет. После добавления каталога `tests/` запускайте набор командой:

```bash
uv run pytest
```

## Технологии

- FastAPI и Uvicorn — HTTP API и ASGI-сервер;
- Dishka — dependency injection;
- Pydantic и pydantic-settings — DTO и конфигурация;
- AsyncPG — асинхронная работа с PostgreSQL;
- HTTPX — исходящие HTTP-запросы;
- Tenacity — retry policy;
- Loguru — логирование;
- uv — управление зависимостями и запуск команд;
- Ruff и ty — форматирование, линтинг и статическая проверка типов.
