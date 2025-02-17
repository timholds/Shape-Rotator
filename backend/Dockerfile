FROM python:3.10-slim

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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements_backend.txt .
RUN pip install --no-cache-dir -r requirements_backend.txt

# Install Manim
RUN pip install manim

# Copy backend code
COPY backend.py collect_data.py ./
COPY system_prompt.txt ./

# Create necessary directories
RUN mkdir -p media training_data

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]