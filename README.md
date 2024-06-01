![repo size](https://img.shields.io/github/repo-size/foxygen-d/cat_charity_fund)
![py version](https://img.shields.io/pypi/pyversions/3)
-----
[![Python](https://img.shields.io/badge/Python-3.9|3.10|3.11-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![pydantic](https://img.shields.io/badge/pydantic-2.6.3-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/pydantic/2.6.3/)
[![backoff](https://img.shields.io/badge/backoff-2.2.1-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/backoff/2.2.1/)

[![fastapi](https://img.shields.io/badge/fastapi-0.110.0-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/fastapi/0.110.0/)
[![fastapi limiter](https://img.shields.io/badge/fastapi_limiter-0.1.6-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/fastapi_limiter/0.1.6/)
[![async_fastapi_jwt_auth](https://img.shields.io/badge/async_fastapi_jwt_auth-0.6.4-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/async_fastapi_jwt_auth/0.6.4/)
[![werkzeug](https://img.shields.io/badge/werkzeug-3.0.2-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/werkzeug/3.0.2/)
[![authlib](https://img.shields.io/badge/authlib-1.3.0-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/authlib/1.3.0/)

[![sqlalchemy](https://img.shields.io/badge/sqlalchemy-2.0.29-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/sqlalchemy/2.0.29/)
[![alembic](https://img.shields.io/badge/alembic-1.13.1-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/alembic/1.13.1/)
[![asyncpg](https://img.shields.io/badge/asyncpg-0.29.0-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/asyncpg/0.29.0/)

[![redis](https://img.shields.io/badge/redis-5.0.3-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/redis/5.0.3)

[![uvicorn](https://img.shields.io/badge/uvicorn-0.28.0-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/uvicorn/0.28.0/)
[![gunicorn](https://img.shields.io/badge/gunicorn-21.2.0-blue?style=flat&logo=python&logoColor=white)](https://pypi.org/project/gunicorn/21.2.0/)


---
[![Poetry](https://img.shields.io/badge/Poetry-used-green?style=flat&logo=python&logoColor=white)](https://pypi.org/project/poetry/)
[![Ruff](https://img.shields.io/badge/Ruff-used-green?style=flat&logo=python&logoColor=white)](https://pypi.org/project/ruff/)
[![pre-commit](https://img.shields.io/badge/pre_commit-used-green?style=flat&logo=python&logoColor=white)](https://pypi.org/project/pre_commit/)


# Auth-Api-For-Portfolio

Сервис открыт из приватного репозитория в качестве портфолио.

## Описание

Сервис авторизации и аутентификации с возможностью работы с JWT токенами и технологией Oauth2.


## Инструкция по развёртыванию проекта

* клонировать проект на компьютер
    ```bash
    git clone git@github.com:MultikPatin/Auth-service.git
    ```
* Установить менеджер зависимостей poetry
    ```bash
    python -m pip install poetry
    ```
* запуск виртуального окружения
    ```bash
    poetry shell
    ```
* установить зависимости
    ```bash
    poetry install --all-extras --with dev --with test
    ```
Сервис реализован в контейнерах Docker  

* запуск docker-compose
    ```bash
    docker-compose up -d -f docker-compose.local.yml
    ```
Для выполнения тестов в контейнерах Docker  

* запуск docker-compose
    ```bash
    docker-compose up -d -f docker-compose.test.yml
    ```
