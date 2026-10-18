FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/workspace/backend:/workspace/mcp-server
WORKDIR /workspace
COPY backend /workspace/backend
COPY mcp-server /workspace/mcp-server
RUN python -m pip install --no-cache-dir -e '/workspace/backend[dev]'
WORKDIR /workspace/mcp-server
CMD ["python", "-m", "sentinel_mcp.server"]
