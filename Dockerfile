# --- Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv for fast, reproducible dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install dependencies into virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# --- Final Production Stage ---
FROM python:3.11-slim AS runtime

WORKDIR /app

# Create a non-root system user for security
RUN groupadd -r atlas && useradd -r -g atlas -s /bin/false atlas

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/2.src"

# Copy source code and documentation
COPY 2.src /app/2.src

# Set permissions
RUN chown -R atlas:atlas /app
USER atlas

# Default command (will run FastAPI gateway from S03 onwards)
CMD ["python", "-c", "import api; print('ATLAS runtime container ready.')"]
