FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace/apps/api:/workspace/apps/worker

WORKDIR /workspace

COPY apps/api/requirements.txt apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

FROM base AS development

COPY apps/api/requirements-dev.txt apps/api/requirements-dev.txt
RUN pip install --no-cache-dir -r apps/api/requirements-dev.txt

COPY . .
CMD ["uvicorn", "gastroledger_api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS runtime

COPY apps/api apps/api
CMD ["uvicorn", "gastroledger_api.app:app", "--host", "0.0.0.0", "--port", "8000"]

