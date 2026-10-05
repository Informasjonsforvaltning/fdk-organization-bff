FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install "poetry==2.5.1"
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.in-project true \
  && poetry install --only main --no-root --no-interaction --no-ansi

FROM python:3.12-slim

ENV TZ=Europe/Oslo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
  && apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

ADD src /app/src

EXPOSE 8080

CMD ["gunicorn", "--chdir", "src", "fdk_organization_bff:create_app", "--config=src/fdk_organization_bff/gunicorn_config.py", "--worker-class", "aiohttp.GunicornWebWorker"]
