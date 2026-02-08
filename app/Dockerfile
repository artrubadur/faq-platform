FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-cache --without=dev

COPY --exclude=__pycache__ ./app ./app
COPY ./config ./config

CMD ["python", "-m", "app.main"]