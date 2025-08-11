# Tensorflow 2.2 requires CUDA 10.1 and cuDNN 7.4
FROM nvcr.io/nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04 AS build

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc wget zlib1g-dev

# DeepSelectNet requires Python 3.5 >= version <= 3.8
# Download and install Python 3.8
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y libffi-dev libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
RUN cd /usr/src && \
    wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz && \
    tar xzf Python-3.8.0.tgz && \
    cd Python-3.8.0 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    ln -s /usr/local/bin/python3.8 /usr/bin/python3 && \
    ln -s /usr/local/bin/pip3.8 /usr/bin/pip3 && \
    cd /usr/src && \
    rm -rf Python-3.8.0.tgz Python-3.8.0

# Clone git repo
RUN apt-get install -y git
RUN git clone https://github.com/AnjanaSenanayake/DeepSelectNet

# Install python libraries
RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org -r ./DeepSelectNet/requirements.txt

# Install tensorflow-gpu to enable GPU
RUN pip install tensorflow-gpu==2.2.0

# Workaround "generated code is out of date and must be regenerated with protoc >= 3.19.0" error in trainer.py
RUN pip install protobuf==3.20.*

# Workaround "module 'numpy' has no attribute 'object'" error in trainer.py
RUN pip install numpy==1.19.5

# Workaround "Matplotlib requires numpy>=1.20; you have 1.19.5" error in trainer.py
RUN pip install matplotlib==3.6

# Workaround Pyslow "ValueError: numpy.ndarray size changed, may indicate binary incompatibility." error in inference.py
# (Rebuild pyslow5 using older numpy)
RUN pip uninstall pyslow5 -y
RUN pip install pyslow5 --no-binary pyslow5

RUN useradd -m user

ENV PATH=$PATH:/app/DeepSelectNet/scripts:/app/DeepSelectNet/support

RUN chmod +x /app/DeepSelectNet/scripts/inference.py
RUN chmod +x /app/DeepSelectNet/scripts/preprocessor.py
RUN chmod +x /app/DeepSelectNet/scripts/trainer.py
RUN sed -i '1i#!/usr/bin/env python3' /app/DeepSelectNet/scripts/inference.py
RUN sed -i '1i#!/usr/bin/env python3' /app/DeepSelectNet/scripts/preprocessor.py
RUN sed -i '1i#!/usr/bin/env python3' /app/DeepSelectNet/scripts/trainer.py

USER user

WORKDIR /workspace
