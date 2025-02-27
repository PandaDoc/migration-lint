FROM python:3.11-slim

ARG version

WORKDIR /app/

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y git curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install migration-lint==$version

ENTRYPOINT ["migration-lint"]