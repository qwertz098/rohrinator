# Rohrinator - Pipe Assembly Generator
# Multi-stage build for smaller image

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libsm6 \
    libice6 \
    libxt6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    cadquery \
    fastapi \
    uvicorn[standard] \
    pydantic

# Production image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libsm6 \
    libice6 \
    libxt6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create app directory
WORKDIR /app

# Copy application code
COPY rohrinator/ /app/rohrinator/

# Create directory for generated files
RUN mkdir -p /tmp/rohrinator

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "rohrinator.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
