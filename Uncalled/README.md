# Quick Start Guide for UNCALLED Docker Image

This Docker image provides a quick and easy way to utilize the `UNCALLED` bioinformatics tool, which rapidly maps raw nanopore signals to a reference sequence. 

The image encapsulates the tool and its dependencies, simplifying setup and usage for end users. This image is maintained independently and is not an official release from the developers of `UNCALLED`.

## Upstream Repository

For comprehensive documentation, feature requests, or to report issues, please refer to the main `UNCALLED` repository at:
[UNCALLED on GitHub](https://github.com/skovaka/UNCALLED)

## Usage Instructions

To use `UNCALLED` through Docker, you can set an alias as follows. This command needs to be executed from the root directory containing your nanopore data, because this is the directory that will be mounted to the containers `/workspace`.

```bash
alias uncalled="docker run --rm -it -v $PWD:/workspace haliliceylanua/uncalled:latest"
```

### Versions

- `ghcr.io/squidbase/uncalled:latest` — upstream v2.3
- `ghcr.io/squidbase/uncalled:v2.0` — version used for the paper's real-data experiments
- `ghcr.io/squidbase/uncalled:v1.0` — published version (Kovaka et al. 2021)

v1.0 and v2.0 need a BWA index built with the bundled `bwa` first
(`bwa index -p <prefix> <fasta>`); v1.0 uses its own CLI
(`uncalled index -i <fasta> -x <prefix>`, `uncalled map -x <prefix> -i <reads>`).

### Basic Examples

1. **Indexing reference sequences**

    Before mapping, you need to build an index of the reference sequences:
	```bash
	uncalled index /workspace/refs/ref.fasta
	```
	
2. **Mapping the reads to the reference**

    After indexing, you can map the nanopore signal data (squiggles) to the reference:
	```bash
    uncalled map -t 48 ref.fasta /workspace/fast5s > uncalled_out.paf
	```

## Remarks

- **Mounting Volumes:** When running the Docker command, ensure that your current working directory (`$PWD`) is mounted correctly to `/workspace` in the container. This setup is crucial for the tool to access data files on your local system.
- **Supported flow cells:** `UNCALLED` is compatible only with legacy r9.4.1 flow cell data.
