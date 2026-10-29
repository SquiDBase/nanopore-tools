# Nanopore_Deep_Learning (Noam Shomron lab) - CPU only, for both training and
# classification. There is no GPU variant: the pipeline this feeds runs on CPU
# nodes, and the code takes --gpu on top of this image unchanged if that changes.
#
# Upstream pins torch==1.8.1 / numpy==1.14.3 / pandas==0.22.0 on Python 3.6.4,
# none of which still build. This image runs current wheels instead; what that
# costs is in cpu_and_cli.patch, and selfcheck.py runs at build time so the
# combination cannot rot silently.
FROM --platform=linux/amd64 python:3.11 AS build

WORKDIR /app

RUN pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# matplotlib: nanopore_training.py writes loss/accuracy plots and imports it at module
# level. ont-fast5-api: read the signal, for nanopore_classify.py only.
RUN pip3 install --no-cache-dir numpy pandas scikit-learn matplotlib ont-fast5-api

ARG UPSTREAM_REF=db57ad6e12d85c60b45794f6636852cbcd81581e
RUN mkdir Nanopore_Deep_Learning && cd Nanopore_Deep_Learning && \
    git init && \
    git remote add origin https://github.com/nshomron/Nanopore_Deep_Learning && \
    git fetch --depth 1 origin ${UPSTREAM_REF} && \
    git checkout FETCH_HEAD && \
    rm -rf .git

COPY cpu_and_cli.patch /tmp/
RUN patch -d /app/Nanopore_Deep_Learning -p1 < /tmp/cpu_and_cli.patch

# Upstream has no offline classifier at all - see nanopore_classify.py's docstring.
COPY nanopore_classify.py selfcheck.py /app/Nanopore_Deep_Learning/

ENV PATH=$PATH:/app/Nanopore_Deep_Learning/
ENV PYTHONPATH=/app/Nanopore_Deep_Learning
# Apptainer keeps the host's HOME, which may be read-only on a compute node;
# matplotlib fails its import-time config write there rather than warning.
ENV MPLCONFIGDIR=/tmp/matplotlib

RUN chmod +x /app/Nanopore_Deep_Learning/*.py && \
    sed -i '1i#!/usr/bin/env python3' /app/Nanopore_Deep_Learning/nanopore_training.py

RUN python3 /app/Nanopore_Deep_Learning/selfcheck.py

RUN useradd -m user
USER user

WORKDIR /workspace
