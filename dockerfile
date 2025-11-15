FROM python:3.13-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -LsS https://astral.sh/uv/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /API-GATEWAY
ENV PATH="/root/.local/bin:$PATH"

COPY . .
RUN uv sync

EXPOSE 8000
CMD ["uv", "run", "--env-file=.env", "main.py"]