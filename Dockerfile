FROM python:3.11-slim

WORKDIR /apps
COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry install

WORKDIR /apps/market

COPY mini_market ./
