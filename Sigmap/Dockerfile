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

ENV HDF5_PLUGIN_PATH=/path/to/hdf5/plugins/lib

RUN git clone https://github.com/haowenz/sigmap \
    && cd sigmap \
    && git checkout c9a4048 \
    && git submodule update --init --recursive --depth 1

RUN cd ./sigmap && make


FROM ubuntu:jammy

RUN useradd -m user

COPY --from=build app/sigmap/sigmap /usr/local/bin/sigmap
COPY --from=build app/sigmap/extern/kmer_models /extern/kmer_models
COPY --from=build app/sigmap/extern/slow5lib /extern/slow5lib

RUN  apt-get update \
  && apt-get install -y wget libgomp1 \
  && rm -rf /var/lib/apt/lists/*

RUN wget -O ont-vbz-hdf-plugin.deb https://github.com/nanoporetech/vbz_compression/releases/download/1.0.2/ont-vbz-hdf-plugin_1.0.2-1.bionic_amd64.deb && \
     apt install -f ./ont-vbz-hdf-plugin.deb && \
     rm -rf ont-vbz-hdf-plugin.deb

ENV HDF5_PLUGIN_PATH=/usr/local/hdf5/lib/plugin/

USER user

WORKDIR /workspace

ENTRYPOINT [] 
