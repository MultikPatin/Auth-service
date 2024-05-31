FROM python:3.11-slim

ENV SRC_PATH '/app'
ENV APP_DIR 'migrations'

WORKDIR $SRC_PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.7.1 \
    && poetry install --extras migrations \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY ./${APP_DIR} ./${APP_DIR}
COPY ./src/core/db/entities ./src/core/db/entities
COPY ./src/core/configs/__init__.py ./src/core/configs/__init__.py
COPY ./src/core/configs/base.py ./src/core/configs/base.py
COPY ./src/core/configs/postgres.py ./src/core/configs/postgres.py
COPY ./src/core/utils/__init__.py ./src/core/utils/__init__.py
COPY ./src/core/utils/sqlalchemy.py ./src/core/utils/sqlalchemy.py
COPY ./alembic.ini ./

RUN chmod +x ${APP_DIR}/entrypoint.sh

ENTRYPOINT ["/bin/bash", "-c", "exec ${SRC_PATH}/${APP_DIR}/entrypoint.sh"]
