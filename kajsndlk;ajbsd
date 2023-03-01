FROM python:3.8-slim-buster

# Exit immediately if a command exits with a non-zero status.
RUN set -e

ENV VIRTUAL_ENV=/env \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY ./ ./

RUN apt update && apt install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-pip \
    python3-dev

RUN pip install --upgrade pip
RUN pip install -r requirements/local.txt



EXPOSE 8000
