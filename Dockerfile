# Stage 1 — build the Next.js application
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline

COPY frontend/ ./
RUN npm run build

# Stage 2 — production Next.js runner
FROM node:20-alpine AS frontend

WORKDIR /app/frontend

ENV NODE_ENV=production

COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder /app/frontend/public ./public

EXPOSE 3000
CMD ["node", "server.js"]

# ────────────────────────────────────────────────────────────
# Backend — FastAPI
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend

WORKDIR /app

# System dependencies required by some packages (e.g. python-magic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY pyproject.toml ./

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
