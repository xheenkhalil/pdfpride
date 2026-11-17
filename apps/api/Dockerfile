FROM python:3.11-slim

# Install system dependencies for document engines (qpdf, Ghostscript, LibreOffice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    qpdf \
    ghostscript \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user for sandboxed security (non-root)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /data/storage /app && \
    chown -R appuser:appuser /data/storage /app

WORKDIR /app

# Copy dependency manifest and install Python wheels
COPY apps/api/requirements.txt /app/apps/api/requirements.txt
RUN pip install --no-cache-dir -r /app/apps/api/requirements.txt

# Copy monorepo packages and API source code
COPY packages /app/packages
COPY apps/api /app/apps/api

RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PYTHONPATH=/app
ENV PORT=8000
ENV LOCAL_STORAGE_DIR=/data/storage

EXPOSE 8000

CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
