# Quick Start Guide for the DeepSelectNet Docker image

This Docker image provides an efficient way to utilize the `DeepSelectNet` bioinformatics tool. `DeepSelectNet` is a proof-of-concept tool designed to classify raw nanopore signals as target or non-target for selective sequencing.

The image contains the tool and its dependencies, simplifying setup and usage for end users. This image is maintained independently and is not an official release from the developers of `DeepSelectNet`.

## Upstream repository

For comprehensive documentation, feature requests, or to report issues, please refer to the main `DeepSelectNet` repository at:
[DeepSelectNet on GitHub](https://github.com/AnjanaSenanayake/DeepSelectNet/)

## Usage instructions

### Setting an alias and running commands

To use `DeepSelectNet` via Docker, you can set an alias as follows. This command needs to be executed from the root directory containing your nanopore data, because this is the directory that will be mounted to the containers' `/workspace/`.
```bash
alias deepselectnet="docker run --rm -it --gpus all -v $PWD:/workspace lraes/deepselectnet:latest"
```

In the Docker image, the `scripts` and `support` directories were added to the path environment variable, and a Python shebang line was added to the beginning of each Python script in those directories. This allows you to execute the scripts in those directories as follows:
```bash
deepselectnet <name_of_script> <commandline arguments>"
```

### GPU acceleration

This Docker container is able to use GPU acceleration by NVIDIA GPUs. To enable this, you need to install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

If you want to run `DeepSelectNet` on CPU, this is possible by removing the `--gpus all` flag from the alias command.

### Examples

1. **Training a model:**

	The training data first needs to be converted to the `slow5` or `blow5` file format. Then it needs to be partitioned into a training + validation partition, and a testing partition. The `DeepSelectNet` authors provide support script to help with these tasks, more information can be found on [the DeepSelectNet GitHub](https://github.com/AnjanaSenanayake/DeepSelectNet/).
	
	The `slow5` or `blow5` training data file can then be used as input for the `preprocessor.py` script:
	```bash
	deepselectnet preprocessor.py -pos_s5 /workspace/data/train-covid.blow5 -neg_s5 /workspace/data/train-zymo.blow5 -b 20000 -c 1500 -sco 4 -mad 3 -o /workspace/output/train
	```
	The numpy tensors that are outputted by this script, can then be used as input for the `trainer.py` script:
	```bash
	deepselectnet trainer.py -d /workspace/output/train -s 0.7 -k 1 -e 200 -o /workspace/output/model
	```
	Remark: the script crashes if the output directory is an existing directory, it needs to create this itself.
	
2. **Classification:**

	The trained model can then be used to classify testing data:
	```bash
	deepselectnet inference.py -model /workspace/output/model -s5 /workspace/data/test-zymo.blow5 -lb 1 -mad 3 -o /workspace/output/classification_zymo
	```
	Remark: only one `blow5` file can be processed per command.
