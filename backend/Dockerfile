# Frontend build stage
FROM node:22-alpine AS frontend-build

# Set working directory
WORKDIR /app

# Set npm registry
RUN npm config set registry https://registry.npmmirror.com/

# Copy frontend files
COPY ../frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY ../frontend/ ./
RUN npm run build

# Backend runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# Update apt sources and install system dependencies
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libsndfile1 \
        ffmpeg \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Verify uv installation
RUN uv --version

# Copy dependency files
COPY backend/pyproject.toml ./

# Sync dependencies using uv
RUN uv pip install -r pyproject.toml --system --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Copy application code
COPY . .

# Copy frontend build from frontend-build stage
COPY --from=frontend-build /app/build ./static

# Create required directories
RUN mkdir -p uploads output

# Expose application port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
