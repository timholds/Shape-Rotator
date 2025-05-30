# Multi-stage build for Python backend
FROM python:3.10-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libffi-dev \
    libgirepository1.0-dev \
    pkg-config \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements_backend.txt .
RUN pip install --no-cache-dir -r requirements_backend.txt 

# Install Manim
RUN pip install manim

# Development stage
FROM base AS development

# Install additional development tools
RUN apt-get update && apt-get install -y \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend.py collect_data.py spaces_storage.py ./ 
COPY system_prompt.txt ./

# Create necessary directories
RUN mkdir -p media training_data

EXPOSE 8000

# Start development server with hot reload
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy backend code
COPY backend.py collect_data.py spaces_storage.py ./ 
COPY system_prompt.txt ./

# Create necessary directories and set permissions
RUN mkdir -p media training_data && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Start production server
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]