FROM continuumio/miniconda3

# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]



RUN useradd -m user

USER user

WORKDIR /app

# Clone ReadCurrent
RUN git clone https://github.com/Ming-Ni-Group/ReadCurrent.git /app/ReadCurrent

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Initialize conda in bash config files:
RUN conda init bash

# Activate the environment
RUN conda activate env_ReadCurrent



# Enabling easy access to scripts and tools
ENV PATH=$PATH:/app/ReadCurrent:/app/ReadCurrent/tools
RUN chmod +x /app/ReadCurrent/tester.py /app/ReadCurrent/preprocessor.py /app/ReadCurrent/trainer.py
RUN sed -i '1i#!/usr/bin/env python3'  /app/ReadCurrent/tester.py
RUN sed -i '1i#!/usr/bin/env python3' /app/ReadCurrent/preprocessor.py
RUN sed -i '1i#!/usr/bin/env python3' /app/ReadCurrent/trainer.py


WORKDIR /workspace
