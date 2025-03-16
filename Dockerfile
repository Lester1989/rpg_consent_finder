# The builder image, used to build the virtual environment
FROM python:3.13-slim AS builder


RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /src

COPY pyproject.toml poetry.lock ./
RUN touch readme.md

RUN poetry install --no-root --without dev && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.13-slim AS runtime
RUN apt-get update && apt-get install libpq5 -y; apt-get -y install curl
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/src/.venv \
    PATH="/src/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src ./src
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
RUN mkdir /db