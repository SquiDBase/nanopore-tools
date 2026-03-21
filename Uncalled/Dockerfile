# Its not possible to use in arm64
FROM --platform=linux/amd64 python:3.6 as build

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc wget

COPY UNCALLED /app

RUN pip install --user .

# Download and install VBZ HDF5 plugin
RUN mkdir -p /vbz_plugin && \
    cd /vbz_plugin && \
    wget -q https://github.com/nanoporetech/vbz_compression/releases/download/v1.0.1/ont-vbz-hdf-plugin-1.0.1-Linux-x86_64.tar.gz && \
    tar -xzf ont-vbz-hdf-plugin-1.0.1-Linux-x86_64.tar.gz && \
    rm ont-vbz-hdf-plugin-1.0.1-Linux-x86_64.tar.gz

FROM --platform=linux/amd64 python:3.6-slim

# Install procps for 'ps' command needed by Nextflow
RUN apt-get update && \
    apt-get install -y --no-install-recommends procps && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m user

COPY --chown=user:user --from=build /root/.local /home/user/.local
COPY --from=build /vbz_plugin/ont-vbz-hdf-plugin-1.0.1-Linux /usr/local/

# Set environment variables for Python and HDF5
ENV PATH=/home/user/.local/bin:$PATH
ENV PYTHONPATH=/home/user/.local/lib/python3.6/site-packages
ENV HDF5_PLUGIN_PATH=/usr/local/usr/local/hdf5/lib/plugin

USER user

WORKDIR /workspace

ENTRYPOINT []
