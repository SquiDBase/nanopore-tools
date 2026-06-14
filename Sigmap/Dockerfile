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

ARG UPSTREAM_REF=c9a40483264c9514587a36555b5af48d3f054f6f
RUN mkdir sigmap && cd sigmap \
    && git init . \
    && git remote add origin https://github.com/haowenz/sigmap \
    && git fetch --depth 1 origin ${UPSTREAM_REF} \
    && git checkout FETCH_HEAD \
    && git submodule update --init --recursive --depth=1

# --- Portability fix (see RawHash2/Dockerfile for rationale) ---------------
# sigmap's Makefile hardcodes -march=native in cxxflags. Patch in-place.
ARG TARGET_ARCH=x86-64-v3
RUN grep -rl 'march=native' sigmap | xargs sed -i "s/-march=native/-march=${TARGET_ARCH}/g"

RUN cd ./sigmap && make

RUN objdump -d sigmap/sigmap \
      | grep -qiE '%zmm[0-9]|kmov[bwdq]|vpcompress|vpternlog|vpconflict|vpexpand' \
      && { echo 'ERROR: AVX-512 instructions present in sigmap'; exit 1; } \
      || echo 'OK: sigmap is portable (no AVX-512)'


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
