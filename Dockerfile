# ========================================================
# Stage 1: Build Vue 3 Frontend
# ========================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

# Cache npm dependencies layer
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline --no-audit

# Copy frontend source code and build production bundle
COPY frontend/ ./
RUN npm run build

# ========================================================
# Stage 2: Backend Runtime & Static Serving
# ========================================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cache Python dependencies layer
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy compiled frontend bundle into backend static directory
COPY --from=frontend-builder /frontend/dist /code/frontend/dist

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--proxy-headers", "--forwarded-allow-ips", "*"]
