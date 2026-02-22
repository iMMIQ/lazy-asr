# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Optional: Use ARG for configurable index URL (default to no proxy for international use)
ARG INDEX_URL=""
ARG TRUSTED_HOST=""

# Install runtime dependencies only (no build tools needed for production)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libsndfile1 \
        ffmpeg \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official method
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Verify uv installation
RUN uv --version

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN if [ -n "$INDEX_URL" ]; then \
        uv pip install system --frozen --index-url "$INDEX_URL"; \
    else \
        uv pip install system --frozen; \
    fi

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p uploads output

# Expose application port
EXPOSE 8000

# Health check (endpoint is at /api/v1/asr/health)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/asr/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
