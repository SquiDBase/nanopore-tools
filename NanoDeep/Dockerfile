FROM python:3.9-slim

WORKDIR /app

# git: shallow-fetch the pinned upstream commit (same pattern as the other images).
# build-essential/python3-dev: several of NanoDeep's pinned dependencies
# (minknow-api's grpcio, ont-fast5-api) still build from source on python 3.9.
# procps: Nextflow needs ps to poll a task's processes.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    python3-dev \
    procps \
 && rm -rf /var/lib/apt/lists/*

# laura-raes/NanoDeep, not lysovosyl/NanoDeep upstream: the fork carries the fixes this
# benchmark needs - per-read prediction output, the *_nostats entry points that do not
# require a label directory, the read-id/prediction alignment fix, and CPU support in
# both the test and the train scripts. Nothing of NanoDeep's own method is changed.
ARG UPSTREAM_REF=5a7d6e9f7e615b1c8102bb00f2219c84db064ba2
RUN mkdir -p /app/NanoDeep && cd /app/NanoDeep && \
    git init . && \
    git remote add origin https://github.com/laura-raes/NanoDeep && \
    git fetch --depth 1 origin ${UPSTREAM_REF} && \
    git checkout FETCH_HEAD && \
    rm -rf .git

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ./NanoDeep

# Create a non-root user
RUN useradd -m user

USER user
WORKDIR /workspace

ENTRYPOINT []
