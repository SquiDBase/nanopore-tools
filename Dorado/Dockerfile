# This Dockerfile deviates from the repo's usual `ARG UPSTREAM_REF` +
# shallow-`git fetch` pattern (see the root README's "Upstream source
# pinning" section): dorado is distributed by ONT only as a prebuilt tarball
# on the ONT CDN, not built from a buildable source tree - building it from
# source would drag in CUDA and libtorch build toolchains for no benefit, so
# it is pinned by release version instead.
FROM debian:bookworm-slim AS build

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates bzip2 \
 && rm -rf /var/lib/apt/lists/*

# Version pin. 2.1.2 is the current release; 0.9.6 is the last release before
# dorado 1.0 deprecated R9.4.1 / R10.4.1 4 kHz / RNA002 (see Dorado/README.md
# and docs/dorado_fast_plan.md for the chemistry table this pin exists for).
ARG DORADO_VERSION=2.1.2
RUN curl -fsSL "https://cdn.oxfordnanoportal.com/software/analysis/dorado-${DORADO_VERSION}-linux-x64.tar.gz" \
    | tar -xz -C /opt \
    && mv "/opt/dorado-${DORADO_VERSION}-linux-x64" /opt/dorado
# Nothing to strip here: the dorado binary statically links the bundled
# libtorch, which is the bulk of the ~3.5 GB tarball.

# minimap2, for the mapping half of DORADO_CLASSIFY (dorado emits BAM/SAM,
# never PAF - see docs/dorado_fast_plan.md). Fetched as a prebuilt release
# tarball rather than compiled, same reasoning as dorado above: no source
# build needed for a portable binary. Keep only the `minimap2` executable -
# the tarball also ships k8/paftools.js, which nothing here uses.
ARG MINIMAP2_VERSION=2.31
RUN curl -fsSL "https://github.com/lh3/minimap2/releases/download/v${MINIMAP2_VERSION}/minimap2-${MINIMAP2_VERSION}_x64-linux.tar.bz2" \
    | tar -xj -C /tmp \
    && mv "/tmp/minimap2-${MINIMAP2_VERSION}_x64-linux/minimap2" /usr/local/bin/minimap2

# Bake models into the image rather than downloading them at runtime: HPC
# compute nodes have no outbound network, and `dorado basecaller fast
# --models-directory /models` needs the right model already sitting on disk
# for whatever chemistry/sample-rate combination the input pod5 carries.
#
# `${DORADO_MODELS:-<default list>}` is evaluated by the shell inside this
# RUN, not declared as the ARG's own default above - that lets the CI matrix
# (.github/workflows/docker.yml) pass a different, 0.9.6-compatible model
# list via --build-arg for the `dorado-legacy` image, without this Dockerfile
# needing a second near-identical copy of itself.
#
# Default list is 2.1.2, fast simplex models only, never `--model all` (that
# pulls every accuracy tier of every chemistry - tens of GB). One entry per
# chemistry this pipeline runs against on the newer (non-deprecated) line -
# see the chemistry table in docs/dorado_fast_plan.md.
ARG DORADO_MODELS=""
RUN mkdir -p /models \
    && MODELS="${DORADO_MODELS:-dna_r10.4.1_e8.2_400bps_fast@v4.2.0 dna_r10.4.1_e8.2_400bps_fast@v4.3.0 dna_r10.4.1_e8.2_400bps_fast@v5.0.0 dna_r10.4.1_e8.2_400bps_fast@v5.2.0 rna004_130bps_fast@v3.0.1 rna004_130bps_fast@v5.0.0 rna004_130bps_fast@v5.1.0 rna004_130bps_fast@v5.2.0 rna004_130bps_fast@v5.3.0 rna004_fast@v6.0.0}" \
    && for m in $MODELS; do \
           /opt/dorado/bin/dorado download --models-directory /models --model "$m"; \
       done \
    # Fail the build rather than ship an image that silently basecalls
    # nothing (dorado's model auto-selection has no fallback: a missing
    # model for the pod5's chemistry is a hard error at basecall time, not
    # build time, so catch it here instead).
    && [ -n "$(ls -A /models)" ] || { echo "ERROR: no dorado models were downloaded into /models" >&2; exit 1; }


FROM debian:bookworm-slim

RUN useradd -m user

COPY --from=build /opt/dorado /opt/dorado
COPY --from=build /models /models
COPY --from=build /usr/local/bin/minimap2 /usr/local/bin/minimap2

ENV PATH=/opt/dorado/bin:$PATH

USER user

WORKDIR /workspace

# For nextflow compatibility (https://github.com/nextflow-io/nextflow/issues/33)
# and because DORADO_CLASSIFY invokes `dorado` and `minimap2` by name, the same
# way every other image in this repo is invoked - see the root README.
ENTRYPOINT []
