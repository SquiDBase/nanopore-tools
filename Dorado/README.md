# Quick Start Guide for Dorado Docker Images

This Docker image provides a quick and easy way to utilize `dorado`, Oxford
Nanopore's own basecaller, together with `minimap2` for mapping.

The image encapsulates the tools and their dependencies, simplifying setup
and usage for end users. This image is maintained independently and is not
an official release from Oxford Nanopore Technologies.

## Upstream Repository

For comprehensive documentation, feature requests, or to report issues,
please refer to the main `dorado` repository at:
[nanoporetech/dorado on GitHub](https://github.com/nanoporetech/dorado)

## Two variants, one chemistry table

Dorado 1.0.0 deprecated basecalling for R9.4.1, R10.4.1 4 kHz sampling, and
RNA002 and never brought them back (`throw_on_deprecated_model` turns any
request for one into a hard error from that release on). The last release
that still basecalls them is 0.9.6. So this directory builds two images from
one Dockerfile, differing only in `dorado` version and baked-in models. The
version is part of the image name, not a `-legacy` suffix, because a third
dorado line is only a matter of time and the version belongs in the name
when that happens:

| chemistry | newest `fast` model | image |
|---|---|---|
| R10.4.1 400bps 5 kHz | `dna_r10.4.1_e8.2_400bps_fast@v5.2.0` | `dorado-v212` (2.1.2) |
| RNA004 | `rna004_fast@v6.0.0` | `dorado-v212` (2.1.2) |
| R10.4.1 400bps 4 kHz | `dna_r10.4.1_e8.2_400bps_fast@v4.1.0` | `dorado-v096` (0.9.6) |
| R9.4.1 | `dna_r9.4.1_e8_fast@v3.4` | `dorado-v096` (0.9.6) |
| R10.4.1 260bps | `dna_r10.4.1_e8.2_260bps_fast@v4.1.0` | `dorado-v096` (0.9.6) |
| RNA002 | `rna002_70bps_fast@v3` | `dorado-v096` (0.9.6) |

`dorado-v096` is not a stale pin: it is the only line that still basecalls
R9.4.1 and 4 kHz R10.4.1 data at all. Pick the image by the chemistry of the
data being basecalled, not by "which is newer".

Every model is baked into `/models` at build time (`dorado download
--models-directory`), because `dorado basecaller fast --models-directory
/models` needs the right model on disk already - the HPC nodes this runs on
have no outbound network, and dorado's own model auto-selection has no
"download it now" fallback.

## Usage Instructions

To use `dorado` and `minimap2` through Docker, you can set an alias as
follows. This command needs to be executed from the root directory
containing your nanopore data, because this is the directory that will be
mounted to the container's `/workspace`. `dorado-v212` is shown below as the
current MinKNOW-equivalent release; swap in `dorado-v096` for the chemistries
in the table above that only it still basecalls.

```bash
alias dorado="docker run --rm -it -v $PWD:/workspace ghcr.io/squidbase/dorado-v212:latest dorado"
```

### Basic Examples

1. **Basecalling pod5 to FASTQ**

    `fast` (the shorthand, not a model name) makes dorado read the
    chemistry and sample rate out of the pod5's own metadata and pick the
    right model out of `/models` itself:
	```bash
	dorado basecaller fast /workspace/pod5s --models-directory /models --emit-fastq -r --device cpu > reads.fastq
	```

2. **Mapping the basecalled reads to a reference**

    Dorado never emits PAF, only BAM/SAM, so mapping is a separate
    `minimap2` step:
	```bash
	minimap2 -x map-ont --secondary=no --paf-no-hit -t 8 ref.mmi reads.fastq > mapped.paf
	```

## Remarks

- **Mounting Volumes:** When running the Docker command, ensure that your
  current working directory (`$PWD`) is mounted correctly to `/workspace` in
  the container. This setup is crucial for the tool to access data files on
  your local system.
- **Supported input format varies by image.** `dorado-v212` (2.1.2) is pod5
  only - FAST5 support was removed upstream in dorado 1.0.0 and never
  restored. `dorado-v096` (0.9.6, pre-1.0) still reads FAST5 as well as pod5,
  though its own loader logs "FAST5 loading is unoptimized and will result in
  poor performance" while doing it, and it refuses a directory holding both
  formats at once. Neither image reads blow5/slow5.
- **CPU-only is supported and is the default here** (`--device cpu`);
  `--device cuda:all` switches to GPU when one is available.
- **Why a tarball, not this repo's usual `git fetch` pattern:** dorado is
  distributed by ONT only as a prebuilt release tarball, not as a buildable
  source tree - building it from source would require pulling in CUDA and
  libtorch build toolchains for no benefit. See `Dockerfile` for the pin.
