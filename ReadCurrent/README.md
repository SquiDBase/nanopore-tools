# Quick Start Guide for ReadCurrent Docker Image

This Docker image provides a quick and easy way to utilize the `ReadCurrent` bioinformatics tool, designed to classify raw nanopore signals as target or non-target for nanopore selective sequencing. 

The image encapsulates the tool and its dependencies, simplifying setup and usage for end users. This image is maintained independently and is not an official release from the developers of `ReadCurrent`.

## Upstream Repository

For comprehensive documentation, feature requests, or to report issues, please refer to the main ReadCurrent repository at:
[ReadCurrent on GitHub](https://github.com/Ming-Ni-Group/ReadCurrent)

## Usage Instructions

To use `ReadCurrent` via Docker, you can set an alias as follows. This command needs to be executed from the root directory containing your nanopore data, because this is the directory that will be mounted to the containers `/workspace`.

```bash
alias readcurrent="docker run --rm -it --gpus all -v $PWD:/workspace lraes/readcurrent conda run --no-capture-output -n env_ReadCurrent"
```

### Basic Examples

1. **Preprocessing data**

    Before training a model, your data needs to be preprocessed. This step converts NumPy array files (`train.npy`, `valid.npy`, and `test.npy`) into a format suitable for the training pipeline.

	> Note: You must generate these .npy files in advance using the read_fast5.py script from the official ReadCurrent repository.

    To preprocess the target reads:
	```bash
	readcurrent preprocessor.py -d /workspace/target_data
	```
	Repeat this step for non-target data, by changing the directory path.
	
2. **Training the model**

    Once preprocessing is complete, you can train the model using the following command:
	```bash
    readcurrent trainer.py -p /workspace/target_data \
        -n /workspace/non-target_data \
        -o $dir_output -g 0 -b 64
	```
	
3. **Testing the model**

    To evaluate a trained model:
    ```bash
    readcurrent tester.py -p /workspace/target_data -n /workspace/non-target_data \
        -ms $model -o $dir_output -g 0 -b 64
    ```

## Remarks

- **Mounting Volumes:** When running the Docker command, ensure that your current working directory (`$PWD`) is mounted correctly to `/workspace` in the container. This setup is crucial for the tool to access data files on your local system.
- **GPU:** The Docker image supports GPU acceleration by default. To run without GPU support, remove the `--gpus all` flag from the alias.
