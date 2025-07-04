FROM ubuntu:jammy AS build

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        cmake \
        build-essential \
        libz-dev \
        libzstd-dev \
        wget \
        libhdf5-serial-dev \
        libhdf5-dev \
        libboost-math-dev \
        git && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/icthrm/cwSDTWnano


RUN cd ./cwSDTWnano/SATnano && \
    rm -rf build && \
    mkdir build && \
    cd build && \
	cmake .. \
	  -DCMAKE_CXX_FLAGS="-I/usr/include/hdf5/serial" \
	  -DCMAKE_EXE_LINKER_FLAGS="-L/usr/lib/x86_64-linux-gnu/hdf5/serial -lhdf5_serial" && \
    make


FROM ubuntu:jammy

RUN useradd -m user

COPY --from=build /app/cwSDTWnano/SATnano/build/bin/sat-query /usr/local/bin/sat-query

RUN  apt-get update \
  && apt-get install -y wget libhdf5-serial-dev \
  && rm -rf /var/lib/apt/lists/*

RUN wget -O ont-vbz-hdf-plugin.deb https://github.com/nanoporetech/vbz_compression/releases/download/1.0.2/ont-vbz-hdf-plugin_1.0.2-1.bionic_amd64.deb && \
     apt install -f ./ont-vbz-hdf-plugin.deb && \
     rm -rf ont-vbz-hdf-plugin.deb

ENV HDF5_PLUGIN_PATH=/usr/local/hdf5/lib/plugin/

USER user

WORKDIR /workspace

# For nextflow compabilitiy https://github.com/nextflow-io/nextflow/issues/33
ENTRYPOINT [] 
