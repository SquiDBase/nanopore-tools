FROM --platform=linux/amd64 oma219/spumoni:v2.0.9 as spumoni

WORKDIR /spumoni

RUN rm -rf build && mkdir build && cd build && cmake .. && make install

FROM --platform=linux/amd64 python:3.9 as build

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc git

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

ARG UPSTREAM_REF=5c6383abcf6db2a1fd5531ecfbfc316c3ab52a6a
RUN git init . \
    && git remote add origin https://github.com/vshiv18/sigmoni \
    && git fetch --depth 1 origin ${UPSTREAM_REF} \
    && git checkout FETCH_HEAD \
    && rm -rf .git

RUN cd src/delta_rust && \
    cargo build --release && \
    mv target/release/libdelta_rust.so ../../delta_rust.so

RUN pip install --user numpy pandas scikit-learn Biopython tqdm

RUN pip install --user git+https://github.com/skovaka/uncalled4

RUN pip install --user tblib

FROM --platform=linux/amd64 python:3.9

RUN useradd -m user

# copy uncalled4
COPY --chown=user:user --from=build /root/.local /home/user/.local
ENV PATH=/home/user/.local/bin:$PATH

# Copy the entire `/spumoni/build` folder into the Docker container
COPY --chown=user:user --from=spumoni /spumoni/build /spumoni/build

# Add `/spumoni/build` to the PATH
ENV PATH="/spumoni/build:$PATH"

# Set SPUMONI_BUILD_DIR environment variable
ENV SPUMONI_BUILD_DIR="/spumoni/build"

# copy sigmoni
COPY --chown=user:user --from=build /app /sigmoni
ENV PATH=/sigmoni:$PATH

RUN chmod +x /sigmoni/index.py && chmod +x /sigmoni/main.py

USER user

WORKDIR /workspace






