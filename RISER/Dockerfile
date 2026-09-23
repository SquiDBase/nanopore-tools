FROM python:3.10-slim AS build

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
 && rm -rf /var/lib/apt/lists/*

# Clone RISER and install requirements
ARG UPSTREAM_REF=d3410a6da26a6fa1222f67ca8d73a48cdc58c6d6
RUN mkdir riser && cd riser && \
    git init && \
    git remote add origin https://github.com/comprna/riser && \
    git fetch --depth 1 origin ${UPSTREAM_REF} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    pip install --upgrade pip && \
    pip install --prefix=/opt/riser -r requirements.txt && \
    pip install --prefix=/opt/riser "pytorch-lightning==2.0.9"

FROM python:3.10-slim

# Create a non-root user
RUN useradd -m user  && \
	apt-get update && apt-get install -y procps

# Copy installed dependencies
COPY --from=build /opt/riser /home/user/.local

# Copy RISER repo (only source code)
COPY --from=build /app/riser /home/user/riser
RUN ln -s /home/user/riser/riser/riser.py /home/user/.local/bin/riser && \
	ln -s /home/user/riser/riser/train.py /home/user/.local/bin/train && \
	ln -s /home/user/riser/riser/test.py /home/user/.local/bin/test && \
	ln -s /home/user/riser/riser/retrain/preprocess.py /home/user/.local/bin/preprocess && \
	ln -s /home/user/riser/riser/retrain/write_tensors.py /home/user/.local/bin/write_tensors && \
	chmod +x /home/user/riser/riser/riser.py /home/user/riser/riser/train.py /home/user/riser/riser/test.py /home/user/riser/riser/retrain/preprocess.py /home/user/riser/riser/retrain/write_tensors.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/riser.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/train.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/test.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/retrain/preprocess.py && \
	sed -i '1i#!/usr/bin/env python3' /home/user/riser/riser/retrain/write_tensors.py

# Restore utilities.py
RUN printf '%s\n' \
	'import attridict' \
	'import yaml' \
	'' \
	'def get_config(filepath):' \
	'    with open(filepath) as config_file:' \
	'        return attridict(yaml.load(config_file, Loader=yaml.Loader))' \
	> /home/user/riser/riser/utilities.py

# test.py computes `device` (cuda if available, else cpu) but then loads the
# checkpoint with a bare torch.load(), so a checkpoint saved on GPU - which the
# released models are - fails to deserialize on a CPU-only node. map_location is
# correct on both devices, so this is a portability fix, not a CPU special case:
# it needs no follow-up when running on GPU. The grep guards the sed - if a
# future UPSTREAM_REF moves this line, the build fails here instead of silently
# shipping the bug again.
RUN grep -q 'load_state_dict(torch\.load(model_file))' /home/user/riser/riser/test.py && \
	sed -i 's/torch\.load(model_file)/torch.load(model_file, map_location=device)/' \
		/home/user/riser/riser/test.py

# Set environment
ENV PATH="/home/user/.local/bin:/home/user/riser/riser:$PATH"
# Explicit, rather than relying on Python's user-site: under Apptainer the
# HOST's $HOME is kept, so ~/.local resolves to the submitting user's home and
# the dependencies copied to /home/user/.local above become invisible - every
# third-party import then fails. Uncalled and BoostNano set it for the same
# reason.
ENV PYTHONPATH="/home/user/.local/lib/python3.10/site-packages"

USER user
WORKDIR /workspace

ENTRYPOINT []
