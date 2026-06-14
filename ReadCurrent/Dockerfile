FROM continuumio/miniconda3

SHELL ["/bin/bash", "--login", "-c"]

WORKDIR /app

# Clone repository
ARG UPSTREAM_REF=6db8921fdc04236dd23a11a951a25ccc0965ae72
RUN mkdir -p /app/ReadCurrent && cd /app/ReadCurrent && \
    git init . && \
    git remote add origin https://github.com/Ming-Ni-Group/ReadCurrent && \
    git fetch --depth 1 origin ${UPSTREAM_REF} && \
    git checkout FETCH_HEAD && \
    rm -rf .git

# Extend tester script to make it more verbose
RUN apt-get update && apt-get install -y patch libgomp1 && rm -rf /var/lib/apt/lists/*
COPY tester_verbose.patch /tmp/
RUN patch --ignore-whitespace --fuzz 3 /app/ReadCurrent/tester.py /tmp/tester_verbose.patch

# Fix CPU compatibility: patch torch.load to handle models trained on GPU
RUN sed -i '/model\.load_state_dict.*torch\.load(args\.model_state)/s/torch\.load(args\.model_state)/torch.load(args.model_state, map_location=torch.device("cpu"))/' /app/ReadCurrent/tester.py

# Create conda env as root
COPY environment.yml .
RUN conda env create -f environment.yml

# Make this env the default python globally
ENV PATH=/opt/conda/envs/env_ReadCurrent/bin:$PATH

# Tools on PATH
ENV PATH=$PATH:/app/ReadCurrent:/app/ReadCurrent/tools

RUN chmod +x /app/ReadCurrent/*.py
RUN sed -i '1i#!/usr/bin/env python3' /app/ReadCurrent/*.py

# Patch old PyTorch version to function on HPC
RUN apt-get update && \
    apt-get install -y patchelf && \
    patchelf --clear-execstack /opt/conda/envs/env_ReadCurrent/lib/python3.9/site-packages/torch/lib/libtorch_cpu.so && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

