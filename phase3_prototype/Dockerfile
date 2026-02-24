# MACP Research Assistant — Phase 3C Production Dockerfile
# ========================================================
# Multi-stage: Node.js frontend build → Python backend + static files
#
# Build context: repo root (run with -f phase3_prototype/Dockerfile .)
# Example: docker build -f phase3_prototype/Dockerfile -t macp-research .

# Stage 1: Frontend build
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY phase3_prototype/frontend/package.json phase3_prototype/frontend/package-lock.json ./
RUN npm ci --production=false
COPY phase3_prototype/frontend/ ./
ENV VITE_API_BASE=""
RUN npm run build

# Stage 2: Backend + static files
FROM python:3.12-slim AS production
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY phase3_prototype/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and tools
COPY phase3_prototype/backend/ ./
COPY tools/ /app/tools/

# Copy MACP schema and agent registry
COPY .macp/schema.json /app/.macp/schema.json
COPY .macp/agents/ /app/.macp/agents/

# Copy frontend build output
COPY --from=frontend-build /app/frontend/dist /app/static

# Create non-root user for security (D-06)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set paths for Docker layout (backend files at /app/, tools at /app/tools/)
ENV TOOLS_DIR=/app/tools
ENV MACP_DIR=/app/.macp
ENV STATIC_DIR=/app/static

# Expose port (Cloud Run uses PORT env var, default 8080)
ENV PORT=8080
EXPOSE 8080

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
