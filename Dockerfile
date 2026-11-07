# Stage 1: Build Frontend React PWA
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python 3.13 Production Runner
FROM python:3.13-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/
COPY pytest.ini ./

# Copy compiled frontend distribution from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Default port
ENV PORT=8000
EXPOSE 8000

# Start command accepting cloud-assigned $PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
