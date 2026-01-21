# ====================
# Stage 1: Builder (simplified - use requirements.txt)
# ====================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ./requirements.txt /build/

# ====================
# Stage 2: Runtime
# ====================
FROM python:3.11-slim AS runtime

WORKDIR /code

# Install runtime dependencies
COPY --from=builder /build/requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /code/app
COPY ./tests /code/tests

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /code
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
