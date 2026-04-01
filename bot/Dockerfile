FROM python:3.12-slim

WORKDIR /bot

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-cache --without=dev

COPY --exclude=__pycache__ ./bot ./bot
COPY ./config ./config

CMD ["python", "-m", "bot.main"]