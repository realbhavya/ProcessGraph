FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY backend/pyproject.toml /tmp/backend-pyproject.toml
RUN mkdir -p /tmp/backend/app && printf '"""installer placeholder"""\n' > /tmp/backend/app/__init__.py \
    && cp /tmp/backend-pyproject.toml /tmp/backend/pyproject.toml \
    && python -m pip install --no-cache-dir '/tmp/backend[dev]'
COPY . /workspace
ENV PYTHONPATH=/workspace/backend
ENTRYPOINT ["bash", "/workspace/scripts/test_m12_container.sh"]
