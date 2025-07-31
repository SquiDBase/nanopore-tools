FROM continuumio/miniconda3

# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]


WORKDIR /app

# Clone ReadCurrent
RUN git clone https://github.com/Ming-Ni-Group/ReadCurrent.git /app/ReadCurrent

# Copy modified tester script
COPY verbose_tester.py /app/ReadCurrent/verbose_tester.py

# Create the environment:
RUN conda env create -f /app/ReadCurrent/environment.yml && \
    conda clean -a -y

# Initialize conda in bash config files:
RUN conda init bash

# Activate environment by default in all future shells
RUN echo "conda activate readcurrent" >> ~/.bashrc


# Enabling easy access to scripts and tools
ENV PATH=$PATH:/app/ReadCurrent:/app/ReadCurrent/tools
RUN chmod +x /app/ReadCurrent/verbose_tester.py /app/ReadCurrent/tester.py /app/ReadCurrent/preprocessor.py /app/ReadCurrent/trainer.py
RUN sed -i '1i#!/usr/bin/env python3'  /app/ReadCurrent/verbose_tester.py
RUN sed -i '1i#!/usr/bin/env python3'  /app/ReadCurrent/tester.py
RUN sed -i '1i#!/usr/bin/env python3' /app/ReadCurrent/preprocessor.py
RUN sed -i '1i#!/usr/bin/env python3' /app/ReadCurrent/trainer.py

WORKDIR /workspace
