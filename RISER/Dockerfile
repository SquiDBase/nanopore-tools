FROM python:3.10.8-slim AS build

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
 && rm -rf /var/lib/apt/lists/*

# Clone RISER and install requirements
ARG UPSTREAM_REF=d3410a6da26a6fa1222f67ca8d73a48cdc58c6d6
RUN mkdir riser && cd riser && \
    git init && \
    git remote add origin https://github.com/comprna/riser && \
    git fetch --depth 1 origin ${UPSTREAM_REF} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    pip install --upgrade pip && \
    pip install --prefix=/opt/riser -r requirements.txt

FROM python:3.10.8-slim

# Create a non-root user
RUN useradd -m user  && \
	apt-get update && apt-get install -y procps

# Copy installed dependencies
COPY --from=build /opt/riser /home/user/.local

# Copy RISER repo (only source code)
COPY --from=build /app/riser /home/user/riser
RUN ln -s /home/user/riser/riser/riser.py /home/user/.local/bin/riser && \
	ln -s /home/user/riser/riser/train.py /home/user/.local/bin/train && \
	ln -s /home/user/riser/riser/test.py /home/user/.local/bin/test && \
	ln -s /home/user/riser/riser/retrain/preprocess.py /home/user/.local/bin/preprocess && \
	ln -s /home/user/riser/riser/retrain/write_tensors.py /home/user/.local/bin/write_tensors && \
	chmod +x /home/user/riser/riser/riser.py /home/user/riser/riser/train.py /home/user/riser/riser/test.py /home/user/riser/riser/retrain/preprocess.py /home/user/riser/riser/retrain/write_tensors.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/riser.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/train.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/test.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/retrain/preprocess.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/retrain/write_tensors.py

# Set environment
ENV PATH="/home/user/.local/bin:/home/user/riser/riser:$PATH"

USER user
WORKDIR /workspace

ENTRYPOINT []
