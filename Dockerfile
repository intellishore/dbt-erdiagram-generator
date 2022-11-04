FROM python:3.9-alpine

COPY . /app

RUN pip install --upgrade pip && pip install /app/src/

WORKDIR /app
