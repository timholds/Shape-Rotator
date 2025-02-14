# Frontend Dockerfile
# ./Dockerfile
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy frontend dependencies
COPY package*.json ./
RUN npm ci

# Copy frontend source
COPY public/ ./public/
COPY src/ ./src/
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    python3-pygments \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6 \
    httpx==0.25.1 \
    moviepy==1.0.3 \
    pydantic==2.4.2 \
    manim

# Copy backend code
COPY backend.py collect_data.py ./
COPY system_prompt.txt ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./static

# Create necessary directories
RUN mkdir -p media training_data

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]