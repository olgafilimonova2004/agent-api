FROM python:3.13-alpine3.24

# для примера
RUN apk add --no-cache \
    ca-certificates

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

ENV UV_CACHE_DIR=/opt/uv-cache/ \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 UV_NO_MANAGED_PYTHON=1
RUN --mount=type=cache,target=/opt/uv-cache uv sync --no-dev --locked --no-install-project

COPY README.md ./
COPY src/ ./src/

RUN --mount=type=cache,target=/opt/uv-cache \
    uv sync --no-dev --locked --no-editable

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["api-base"]
