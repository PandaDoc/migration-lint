FROM python:3.11-slim

WORKDIR /app/

RUN apt-get update -y \
    && apt-get install -y git curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install migration-lint

ENTRYPOINT ["migration-lint"]