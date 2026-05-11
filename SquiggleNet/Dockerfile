# SquiggleNet requires Python >= 3.7
FROM --platform=linux/amd64 python:3.11 AS build

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc git

# PyTorch CPU version (or should the container support GPU?)
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN pip3 install scipy numpy click ont-fast5-api

RUN pip3 install typing-extensions --upgrade

ARG UPSTREAM_REF=fb7b206
RUN mkdir SquiggleNet && cd SquiggleNet && \
    git init && \
    git remote add origin https://github.com/welch-lab/SquiggleNet && \
    git fetch --depth 1 origin ${UPSTREAM_REF} && \
    git checkout FETCH_HEAD && \
    rm -rf .git

RUN useradd -m user

RUN wget -O ont-vbz-hdf-plugin.deb https://github.com/nanoporetech/vbz_compression/releases/download/1.0.2/ont-vbz-hdf-plugin_1.0.2-1.bionic_amd64.deb && \
     apt install -f ./ont-vbz-hdf-plugin.deb && \
     rm -rf ont-vbz-hdf-plugin.deb

ENV HDF5_PLUGIN_PATH=/usr/local/hdf5/lib/plugin/

ENV PATH=$PATH:/app/SquiggleNet/

RUN chmod +x /app/SquiggleNet/inference.py && chmod +x /app/SquiggleNet/preprocess.py && chmod +x /app/SquiggleNet/trainer.py
RUN sed -i '1i#!/usr/bin/env python3' /app/SquiggleNet/inference.py
RUN sed -i '1i#!/usr/bin/env python3' /app/SquiggleNet/preprocess.py
RUN sed -i '1i#!/usr/bin/env python3' /app/SquiggleNet/trainer.py

USER user

WORKDIR /workspace
