FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1

RUN python -m pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main,orchestrator,shared --no-root --no-cache

COPY --exclude=__pycache__ ./orchestrator ./orchestrator
COPY --exclude=__pycache__ ./shared ./shared

EXPOSE 8000

CMD ["python", "-m", "orchestrator"]
