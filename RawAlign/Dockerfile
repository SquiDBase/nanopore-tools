# Its not possible to use in arm64
FROM --platform=linux/amd64 ubuntu:jammy AS build

WORKDIR /app

RUN  apt-get update \
  && apt-get install -y make build-essential libz-dev git \
  && rm -rf /var/lib/apt/lists/*

ARG UPSTREAM_REF=ee59c4e5d04d8464e134fe5c0c9e1cd38ccc9cc3
RUN git init . \
  && git remote add origin https://github.com/cmu-safari/RawAlign \
  && git fetch --depth 1 origin ${UPSTREAM_REF} \
  && git checkout FETCH_HEAD \
    && git submodule update --init --recursive --depth=1

# --- Portability fix (see RawHash2/Dockerfile for rationale) ---------------
# RawAlign's Makefile appends -march=native. Patch only top-level Makefiles,
# not extern submodules, to avoid breaking their build systems.
ARG TARGET_ARCH=x86-64-v3
RUN find . -maxdepth 3 -name 'Makefile' ! -path '*/extern/*' ! -path '*/.git/*' \
  | xargs grep -l 'march=native' \
  | xargs sed -i "s/-march=native/-march=${TARGET_ARCH}/g"

RUN env -u TARGET_ARCH make


FROM --platform=linux/amd64 ubuntu:jammy

RUN useradd -m user

COPY --from=build /app/bin/rawalign /usr/local/bin/rawalign
COPY --from=build /app/extern/kmer_models /extern/kmer_models
COPY --from=build /app/extern/local_kmer_models /extern/local_kmer_models

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN wget -O ont-vbz-hdf-plugin.deb https://github.com/nanoporetech/vbz_compression/releases/download/1.0.2/ont-vbz-hdf-plugin_1.0.2-1.bionic_amd64.deb && \
     apt install -f ./ont-vbz-hdf-plugin.deb && \
     rm -rf ont-vbz-hdf-plugin.deb

ENV HDF5_PLUGIN_PATH=/usr/local/hdf5/lib/plugin/

USER user

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/rawalign"]

# For nextflow compabilitiy https://github.com/nextflow-io/nextflow/issues/33
ENTRYPOINT [] 
