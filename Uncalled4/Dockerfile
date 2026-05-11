# # Its not possible to use in arm64
# FROM --platform=linux/amd64 python:3.11 as build

# WORKDIR /app

# RUN apt-get update
# RUN apt-get install -y --no-install-recommends build-essential gcc

# RUN python -m venv /opt/venv

# # Make sure we use the virtualenv:
# ENV PATH="/opt/venv/bin:$PATH"

# COPY uncalled4 /app

# RUN pip install .


# FROM --platform=linux/amd64 python:3.11-slim

# RUN useradd -m user

# COPY --from=build /opt/venv /opt/venv

# # Make sure we use the virtualenv:
# ENV PATH="/opt/venv/bin:$PATH"

# USER user

# WORKDIR /workspace

# ENTRYPOINT ["uncalled4"]


# Its not possible to use in arm64
FROM --platform=linux/amd64 python:3.11 as build

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc git


ARG UPSTREAM_REF=679e37b62027051e89030dc57619aa7c10d7115a
RUN git init . \
    && git remote add origin https://github.com/skovaka/uncalled4 \
    && git fetch --depth 1 origin ${UPSTREAM_REF} \
    && git checkout FETCH_HEAD

RUN pip install --user .

FROM --platform=linux/amd64 python:3.11-slim

RUN useradd -m user

COPY --chown=user:user --from=build /root/.local /home/user/.local
ENV PATH=/home/user/.local/bin:$PATH
USER user

WORKDIR /workspace

ENTRYPOINT ["uncalled4"]