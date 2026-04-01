FROM python:3.12-slim

WORKDIR /bot

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1

RUN python -m pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main,bot,shared --no-root --no-cache

COPY --exclude=__pycache__ ./bot ./bot
COPY --exclude=__pycache__ ./shared ./shared

CMD ["python", "-m", "bot.main"]
