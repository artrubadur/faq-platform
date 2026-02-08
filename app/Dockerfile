FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry install --without=dev

COPY ./app ./app
COPY ./config ./config

CMD ["python", "-m", "app.main"]