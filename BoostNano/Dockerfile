FROM python:3.10-slim AS build

WORKDIR /app

# boostnano ships a C++ extension (hmm.cpp) and only an sdist on PyPI, so it is
# compiled here rather than pulled as a wheel.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# boostnano's setup.py declares no install_requires at all, so every runtime
# dependency is named here instead. Its requirements.txt also lists PyQt5, which
# only the hand_label.py GUI needs - boostnano_eval.py does not, so it is left out.
# vbz-h5py-plugin is not in that list either, but boostnano_eval.py opens fast5
# with plain h5py, and ONT writes VBZ-compressed signal: without the plugin every
# read fails with "can't open directory (/usr/local/lib/plugin)".
# CPU torch: BoostNano's CSM is a small model and these jobs run on CPU partitions.
#
# numpy is pinned below 2 on purpose: hmm.cpp uses PyArray_FLOAT/DOUBLE/SHORT/LONG,
# legacy C-API aliases numpy 2 removed, so it does not compile against numpy 2 and
# the extension's ABI is numpy 1.x. Build isolation is disabled so that pin is the
# one the extension is compiled against rather than whatever pyproject.toml resolves.
ARG BOOSTNANO_VERSION=0.1.4
RUN pip install --upgrade pip && \
    pip install --prefix=/opt/boostnano \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        "numpy<2" torch torchvision h5py scipy matplotlib tqdm vbz-h5py-plugin && \
    pip install --prefix=/opt/boostnano setuptools cython && \
    PYTHONPATH=/opt/boostnano/lib/python3.10/site-packages \
    pip install --prefix=/opt/boostnano --no-build-isolation \
        boostnano==${BOOSTNANO_VERSION}

FROM python:3.10-slim

RUN useradd -m user && \
    apt-get update && apt-get install -y --no-install-recommends procps && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/boostnano /home/user/.local

# boostnano_eval.py is a module inside the package, not a console_script, so it
# is linked onto PATH the way the RISER image links RISER's scripts.
RUN SP=$(ls -d /home/user/.local/lib/python3.*/site-packages) && \
    sed -i '1i#!/usr/bin/env python3' "$SP/boostnano/boostnano_eval.py" && \
    chmod +x "$SP/boostnano/boostnano_eval.py" && \
    ln -s "$SP/boostnano/boostnano_eval.py" /home/user/.local/bin/boostnano_eval.py

# The PyPI sdist bundles the trained checkpoint under boostnano/model, so the
# -m/--model_path argument has a fixed location inside the image.
ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONPATH="/home/user/.local/lib/python3.10/site-packages" \
    HDF5_PLUGIN_PATH="/home/user/.local/lib/python3.10/site-packages/vbz_h5py_plugin/lib" \
    BOOSTNANO_MODEL="/home/user/.local/lib/python3.10/site-packages/boostnano/model"

USER user
WORKDIR /workspace

ENTRYPOINT []
