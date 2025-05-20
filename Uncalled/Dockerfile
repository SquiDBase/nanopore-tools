# Its not possible to use in arm64
FROM --platform=linux/amd64 python:3.6 as build

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc


COPY UNCALLED /app

RUN pip install --user .

FROM --platform=linux/amd64 python:3.6-slim

RUN useradd -m user

COPY --chown=user:user --from=build /root/.local /home/user/.local
ENV PATH=/home/user/.local/bin:$PATH
USER user

WORKDIR /workspace

ENTRYPOINT []