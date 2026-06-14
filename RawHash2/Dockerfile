FROM ubuntu:jammy AS build

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        make \
        build-essential \
        libz-dev \
        libzstd-dev \
        wget \
        git && \
    rm -rf /var/lib/apt/lists/*

ARG UPSTREAM_REF=d3956eaf261588555fa884c5c294fd46df591851
RUN mkdir RawHash && cd RawHash \
    && git init . \
    && git remote add origin https://github.com/CMU-SAFARI/RawHash \
    && git fetch --depth 1 origin ${UPSTREAM_REF} \
    && git checkout FETCH_HEAD \
    && git submodule update --init --recursive --depth=1

# --- Portability fix -------------------------------------------------------
# Upstream src/Makefile hardcodes -march=native. Target only that file so the
# zstd extern submodule build is not disrupted.
ARG TARGET_ARCH=x86-64-v3
RUN sed -i "s/-march=native/-march=${TARGET_ARCH}/g" RawHash/src/Makefile

RUN cd ./RawHash && make


FROM ubuntu:jammy

RUN useradd -m user

COPY --from=build app/RawHash/bin/rawhash2 /usr/local/bin/rawhash2
COPY --from=build app/RawHash/extern/kmer_models /extern/kmer_models
COPY --from=build app/RawHash/extern/local_kmer_models /extern/local_kmer_models

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN wget -O ont-vbz-hdf-plugin.deb https://github.com/nanoporetech/vbz_compression/releases/download/1.0.2/ont-vbz-hdf-plugin_1.0.2-1.bionic_amd64.deb && \
     apt install -f ./ont-vbz-hdf-plugin.deb && \
     rm -rf ont-vbz-hdf-plugin.deb

ENV HDF5_PLUGIN_PATH=/usr/local/hdf5/lib/plugin/

USER user

WORKDIR /workspace

#ENTRYPOINT ["/usr/local/bin/rawhash2"]

# For nextflow compabilitiy https://github.com/nextflow-io/nextflow/issues/33
ENTRYPOINT [] 
