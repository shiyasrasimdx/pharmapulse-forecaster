# Stage 1: Build Vite React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Flask Backend + Serve Frontend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy dataset & backend code
COPY "SHAFI HAJI JAN2026TOAUG2026(1).xlsx" .
COPY backend/ ./backend/

# Copy built frontend assets to static directory served by Flask
COPY --from=frontend-builder /app/frontend/dist ./backend/static

EXPOSE 5000

ENV PORT=5000
CMD ["gunicorn", "--chdir", "backend", "app:app", "--bind", "0.0.0.0:5000"]
