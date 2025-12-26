# The builder image
FROM python:3.13-slim AS builder

RUN pip install poetry==2.2.1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /src

COPY pyproject.toml poetry.lock ./
RUN touch readme.md

# 1. Install app deps
RUN poetry install --no-root


# 2. Bootstrap: This installs the sensors for FastAPI, SQLAlchemy, etc.
RUN ./.venv/bin/opentelemetry-bootstrap -a install

RUN rm -rf $POETRY_CACHE_DIR


# The runtime image
FROM python:3.13-slim AS runtime
RUN apt-get update && apt-get install libpq5 -y; apt-get -y install curl

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/src/.venv \
    PATH="/src/.venv/bin:$PATH"

# Copy the venv that now includes OTel and all instrumentations
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
RUN mkdir /db

# The PATH env above ensures 'opentelemetry-instrument' is found automatically