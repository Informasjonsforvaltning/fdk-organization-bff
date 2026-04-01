FROM python:3.12-slim

ENV TZ=Europe/Oslo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

RUN pip install "poetry==2.3.3"
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-root --no-interaction --no-ansi

ADD src /app/src

EXPOSE 8080

CMD ["gunicorn", "--chdir", "src", "fdk_organization_bff:create_app", "--config=src/fdk_organization_bff/gunicorn_config.py", "--worker-class", "aiohttp.GunicornWebWorker"]
