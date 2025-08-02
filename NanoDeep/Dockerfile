FROM python:3.9-slim

WORKDIR /app

# Install curl, tar, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tar \
    build-essential \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Download NanoDeep snapshot
ADD https://github.com/lysovosyl/NanoDeep/archive/1abba04.tar.gz /app/

# Extract and rename folder
RUN tar xzf 1abba04.tar.gz && \
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
