FROM python:3.13-slim-bookworm

# Install runtime dependencies + build tools in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -LsS https://astral.sh/uv/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Set up environment and working directory
WORKDIR /API-GATEWAY
ENV PATH="/root/.local/bin:$PATH"

# Copy application code and install dependencies
COPY . .
RUN uv sync

# Runtime configuration
EXPOSE 8000
CMD ["uv", "run", "--env-file=.env", "main.py"]