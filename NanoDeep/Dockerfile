FROM python:3.9-slim

WORKDIR /app

# Install curl, tar, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tar \
    build-essential \
    python3-dev \
    procps \
 && rm -rf /var/lib/apt/lists/*

# Download the latest version of NanoDeep's benchmarking fork
ADD https://github.com/laura-raes/NanoDeep/archive/refs/heads/main.tar.gz /app/

# Extract and rename folder
RUN tar xzf main.tar.gz && \
    mv NanoDeep-* NanoDeep

# Upgrade pip and install NanoDeep with dependencies
RUN pip install --upgrade pip && \
    pip install ./NanoDeep

# Add installed scripts to PATH
ENV PATH="/usr/local/bin:$PATH"

# Create a non-root user
RUN useradd -m user

USER user
WORKDIR /workspace

ENTRYPOINT []
