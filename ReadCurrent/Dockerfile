FROM continuumio/miniconda3

SHELL ["/bin/bash", "--login", "-c"]

WORKDIR /app

# Clone repository
RUN git clone https://github.com/Ming-Ni-Group/ReadCurrent.git /app/ReadCurrent

# Extend tester script to make it more verbose
RUN apt-get update && apt-get install -y patch && rm -rf /var/lib/apt/lists/*
COPY tester_verbose.patch /tmp/
RUN patch --ignore-whitespace --fuzz 3 /app/ReadCurrent/tester.py /tmp/tester_verbose.patch

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

# Drop privileges
RUN useradd -m user
USER user

WORKDIR /workspace

