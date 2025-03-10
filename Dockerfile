FROM python:3.12-slim

WORKDIR /app

#install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    export PATH="/opt/poetry/bin:$PATH" && \
    poetry config virtualenvs.create false
# install packages using poetry
COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install --only main --no-interaction --no-ansi

# or use pip method
# RUN apt-get update
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirement.txt

COPY . /app/
RUN chmod +x /app/docker_entrypoint.sh
ENTRYPOINT ["/app/docker_entrypoint.sh"]



