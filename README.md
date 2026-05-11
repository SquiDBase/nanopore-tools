# nanopore-tools

Docker containers for tools used in nanopore signal-level ("squiggle") analysis.

Each top-level directory is a self-contained build for one upstream project.
Images are built by CI and published to GitHub Container Registry.

## Quick start

```
docker pull ghcr.io/squidbase/uncalled:latest
docker run --rm -it ghcr.io/squidbase/uncalled:latest --help
```

## Versioning

Two independent things are pinned for every image:

- **Image tag** — set by CI to the short SHA of this repo at build time, plus
  `:latest`. Format: `ghcr.io/squidbase/<tool>:<short-sha>` and
  `ghcr.io/squidbase/<tool>:latest`. Every push to `main` produces a fresh
  pair; PR builds verify but don't push.
- **Upstream tool pin** — each Dockerfile fetches its upstream source at a
  specific commit via `ARG UPSTREAM_REF=<full-sha>`. Override at build time
  with `--build-arg UPSTREAM_REF=<sha>` (see [Building locally](#building-locally)).

To pin a deployment, use the short-SHA tag (e.g.
`ghcr.io/squidbase/uncalled:9dcb4ea`) rather than `:latest`. The short SHA
identifies the exact Dockerfile and upstream pin used.

## Available tools

All images live under `ghcr.io/squidbase/`. The "Pull" column shows the
matching tag; substitute `:latest` with a specific `<short-sha>` to pin.

### Mapping

| Tool | Upstream | Pull |
|---|---|---|
| UNCALLED | [skovaka/UNCALLED](https://github.com/skovaka/UNCALLED) | `docker pull ghcr.io/squidbase/uncalled:latest` |
| UNCALLED 4 | [skovaka/uncalled4](https://github.com/skovaka/uncalled4) | `docker pull ghcr.io/squidbase/uncalled4:latest` |
| RawAlign | [CMU-SAFARI/RawAlign](https://github.com/CMU-SAFARI/RawAlign) | `docker pull ghcr.io/squidbase/rawalign:latest` |
| RawHash | [CMU-SAFARI/RawHash](https://github.com/CMU-SAFARI/RawHash) | `docker pull ghcr.io/squidbase/rawhash2:latest` |
| Sigmap | [haowenz/sigmap](https://github.com/haowenz/sigmap) | `docker pull ghcr.io/squidbase/sigmap:latest` |

### Classification

| Tool | Upstream | Pull |
|---|---|---|
| Sigmoni | [vshiv18/sigmoni](https://github.com/vshiv18/sigmoni) | `docker pull ghcr.io/squidbase/sigmoni:latest` |
| SquiggleNet | [welch-lab/SquiggleNet](https://github.com/welch-lab/SquiggleNet) | `docker pull ghcr.io/squidbase/squigglenet:latest` |
| ReadCurrent | [Ming-Ni-Group/ReadCurrent](https://github.com/Ming-Ni-Group/ReadCurrent) | `docker pull ghcr.io/squidbase/readcurrent:latest` |
| RISER | [comprna/riser](https://github.com/comprna/riser) | `docker pull ghcr.io/squidbase/riser:latest` |
| DeepSelectNet (CPU) | [AnjanaSenanayake/DeepSelectNet](https://github.com/AnjanaSenanayake/DeepSelectNet) | `docker pull ghcr.io/squidbase/deepselectnet-cpu:latest` |
| DeepSelectNet (GPU) | [AnjanaSenanayake/DeepSelectNet](https://github.com/AnjanaSenanayake/DeepSelectNet) | `docker pull ghcr.io/squidbase/deepselectnet-gpu:latest` |

## Building locally

Each Dockerfile pins its upstream source through an `ARG UPSTREAM_REF`. Build
with the default pin:

```
docker build -t my-uncalled Uncalled
```

…or build against a different upstream commit:

```
docker build --build-arg UPSTREAM_REF=<commit-sha> -t my-uncalled Uncalled
```

## Upstream source pinning

To keep builds reproducible, fast, and free of upstream VCS metadata, every
Dockerfile fetches its tool with a shallow, single-commit fetch of a pinned ref:

```
ARG UPSTREAM_REF=<commit-sha>
RUN git init . \
    && git remote add origin https://github.com/<org>/<repo> \
    && git fetch --depth 1 origin ${UPSTREAM_REF} \
    && git checkout FETCH_HEAD \
    && rm -rf .git
```

Notes:

- Drop `rm -rf .git` if the stage is intermediate and nothing copies the
  working tree into the final image (multi-stage builds that only copy built
  artifacts via `COPY --from=build`).
- Drop `rm -rf .git` if the build needs `.git` later (e.g. `git submodule
  update`). In that case, do the submodule init **before** any subsequent
  removal, or rely on a multi-stage build to discard `.git` for you.
- For repos with submodules, append `&& git submodule update --init
  --recursive --depth=1` to the same RUN.
- Make sure the base image has `git` installed (most slim/distroless ones
  don't — add it to your `apt-get install` or `apk add` list).

## Adding a new tool

Follow these steps to add a new tool to the repo and CI pipeline.

### 1. Create the tool directory

Create a top-level directory named after the tool (PascalCase to match the
upstream project's name is fine — e.g. `NewTool/`). Anything the build needs
that isn't in upstream (patch files, modified scripts, an `environment.yml`)
lives in that directory and is referenced relatively from the Dockerfile.

### 2. Write the Dockerfile

Place `NewTool/Dockerfile` (or `Dockerfile.cpu` / `Dockerfile.gpu` for split
builds). Follow the canonical pattern:

```Dockerfile
FROM <base-image> AS build

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git \
 && rm -rf /var/lib/apt/lists/*

ARG UPSTREAM_REF=<commit-sha>
RUN git init . \
    && git remote add origin https://github.com/<org>/<repo> \
    && git fetch --depth 1 origin ${UPSTREAM_REF} \
    && git checkout FETCH_HEAD \
    && rm -rf .git

# …tool-specific build steps…
```

Conventions:

- Prefer multi-stage builds for compiled tools so the final image only carries
  the built artifacts.
- Add a non-root `user` and `WORKDIR /workspace` in the final stage.
- Pin `UPSTREAM_REF` to a specific commit SHA, not a branch name.

### 3. Wire the tool into CI

Edit `.github/workflows/docker.yml`. Two places need a matching entry — the
**path filter** name and the **matrix** name must be identical.

**a. Path filter** — under `steps.filter.with.filters`, add:

```yaml
newtool:
  - 'NewTool/**'
```

**b. Build matrix** — inside the `ALL` JSON array in the `Build matrix` step,
add an entry:

```json
{"name":"newtool","dockerfile":"NewTool/Dockerfile","context":"NewTool"}
```

If the tool has both CPU and GPU variants (like `DeepSelectNet`), add two
matrix entries and two path filter entries that point to the same directory:

```yaml
newtool-cpu:
  - 'NewTool/**'
newtool-gpu:
  - 'NewTool/**'
```

```json
{"name":"newtool-cpu","dockerfile":"NewTool/Dockerfile.cpu","context":"NewTool"},
{"name":"newtool-gpu","dockerfile":"NewTool/Dockerfile.gpu","context":"NewTool"}
```

The `name` field becomes the image name on GHCR
(`ghcr.io/<owner>/<name>:<tag>`), so pick something short and lowercase.

### 4. Verify the build

- Open a PR. The `detect-changes` job will pick up your new directory via the
  path filter and run the matching matrix entry. PR builds don't push — they
  only verify that the image builds.
- After merge to `main`, the image is built again and pushed to GHCR with both
  `:<short-sha>` and `:latest` tags.

### Triggering a manual build

The workflow also supports `workflow_dispatch`. From the Actions tab, run
"Build and push Docker images" with the `tools` input set to a
comma-separated list of matrix `name`s — or `all` to rebuild everything:

```
all
uncalled,rawalign
deepselectnet-cpu
```
