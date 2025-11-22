# Use Python 3.12 slim image
FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy application code
COPY . .

# Install the project itself
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the application
# We use the virtual environment created by uv
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "python", "-m", "website.app"]
