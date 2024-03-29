# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /usr/src/arcadia_bot

# Update apt-get
RUN apt-get update -y

# Install poetry
ENV POETRY_VERSION=1.4.2
RUN apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install project dependencies via poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install

# Copy application
COPY . .

# Run application
CMD ["poetry", "run", "python", "arcadia_bot/arcadia_bot.py"]
