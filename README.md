# NIST De-ID2 Challenge

![Python 3.8](https://img.shields.io/badge/Python-3.8-blue) [![GPU Docker Image](https://img.shields.io/badge/Docker%20image-gpu--latest-green)](https://hub.docker.com/r/drivendata/sfp-competition/tags?page=1&name=gpu-latest) [![CPU Docker Image](https://img.shields.io/badge/Docker%20image-cpu--latest-lightgrey)](https://hub.docker.com/r/drivendata/sfp-competition/tags?page=1&name=cpu-latest) 

Welcome to the runtime repository for the [NIST De-ID2 Challenge](https://www.drivendata.org/competitions/68/competition-differential-privacy-maps-1). This repo contains the definition of the environment where your code submissions will run. It specifies both the operating system and the Python packages that will be available to your solution.

This repository has two primary uses for competitors:

 - **Testing your code submission**: It lets you test your `submission.zip` file with a locally running version of the container so you don't have to wait for it to process on the competition site to find programming errors.
 - **Requesting new packages in the official runtime**: It lets you test adding additional packages to the [official runtime environment](runtime/py-gpu.yml). The official runtime uses **Python 3.8**. You can then submit a PR to request compatible packages be included in the official container image.

 ----

### [Getting started](#0-getting-started)
 - [Prerequisites](#prerequisites)
 - [Quickstart](#quickstart)
### [Testing your submission.zip](#1-testing-your-submissionzip)
 - [Implement your solution](#implement-your-solution)
 - [How your submission will run](#how-your-submission-will-run)
 - [Test running your submission locally](#test-running-your-submission-locally)
   - [Making a submission](#making-a-submission)
   - [Reviewing the logs](#reviewing-the-logs)
### [Updating the runtime packages](#2-updating-the-runtime-packages)
 - [Adding new Python packages](#adding-dependencies-to-the-runtime)
 - [Testing new dependencies](#testing-new-dependencies)
 - [Submitting a PR](#opening-a-pull-request)

----

## (0) Getting started

### Prerequisites

Make sure you have the prerequisites installed.

 - A clone or fork of this repository
 - [Docker](https://docs.docker.com/get-docker/)
 - At least ~10GB of free space for both the training images and the Docker container images
 - GNU make (optional, but useful for using the commands in the Makefile)

Additional requirements to run with GPU:

 - [NVIDIA drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#package-manager-installation) with CUDA 11 (we check whether you have `nvidia-smi` installed and enabled to automatically determine whether to build the CPU or GPU image)
 - [NVIDIA Docker container runtime](https://nvidia.github.io/nvidia-container-runtime/)

### Quickstart

To test out the full execution pipeline, run the following commands in order in the terminal. These will get the Docker images, zip up an example submission script, and submit that submission.zip to your locally running version of the container.

```
make pull
make pack-benchmark
make test-submission
```

You should see output like this in the end (and find the same logs in the folder `submission/log.txt`):

```
TODO: replace
docker run \
		--network none \
		--mount type=bind,source=/Users/bull/code/sfp-cervical-biopsy-runtime/data,target=/codeexecution/data,readonly \
		--mount type=bind,source=/Users/bull/code/sfp-cervical-biopsy-runtime/submission,target=/codeexecution/submission \
	   	--shm-size 8g \
		925a59ad1b19
GPU unavailable; falling back to CPU.
Unpacking submission...
Archive:  ./submission/submission.zip
   creating: ./assets/
  inflating: ./main.py
Running submission with Python
Exporting submission.csv result...
Script completed its run.
================ END ================
```

Running `make` at the terminal will tell you all the commands available in the repository:

```
TODO: replace
Settings based on your machine:
CPU_OR_GPU=cpu 			# Whether or not to try to build, download, and run GPU versions
SUBMISSION_IMAGE=925a59ad1b19 	# ID of the image that will be used when running test-submission

Available competition images:
drivendata/sfp-competition:cpu-local (925a59ad1b19); drivendata/sfp-competition:cpu-latest (09768914d125);

Available commands:

build               Builds the container locally, tagging it with cpu-local or gpu-local
debug-container     Start your locally built container and open a bash shell within the running container; same as submission setup except has network access
pack-benchmark      Creates a submission/submission.zip file from whatever is in the "benchmark" folder
pull                Pulls the official container tagged cpu-latest or gpu-latest from Docker hub
sample-data         Download TODO
test-container      Ensures that your locally built container can import all the Python packages successfully when it runs
test-submission     Runs container with submission/submission.zip as your submission and data as the data to work with
```

To find out more about what these commands do, keep reading! :eyes:

## (1) Testing your submission.zip

### Implement your solution

In order to test your code submission, you will need a code submission! You will need to train your model separately before creating your `submission.zip` file that will run your code.

**NOTE: You will implement all of your training and experiments on your machine. It is highly recommended that you use the same package versions that are in the runtime ([Python (CPU)](runtime/py-cpu.yml), [Python (GPU)](runtime/py-gpu.yml), [R (CPU)](runtime/r-cpu.yml), or [R (GPU)](runtime/r-gpu.yml)). They can be installed with `conda`.**

The [submission format page](https://www.drivendata.org/competitions/TODO) contains the detailed information you need to prepare your submission.

### How your submission will run

Your submission will run inside a virtual operating system within the container that Docker runs on your machine (your computer is the "host" for the container). Within that virtual operating system, `/codeexecution/data` will point to whatever is in your host machine's `data` folder. `/codeexecution/submission` will point to whatever is in your host machine's `submission` folder.

The script to execute the submission will unzip the contents of `/codeexecution/submission/submssion.zip` into the `/codeexecution` folder. This should create a `main.py`, `main.R`, or `main` executable binary in the `/codeexecution`.

Your code should read the `submission_format.csv` and `TODO.csv` files from `/codeexecution/data`. On the DrivenData platform, `/codeexecution/data` will have the actual test images, and the matching `submission_format.csv` and `TODO.csv`.

As mentioned, when you execute the container locally, we will mount two subfolders in this repository into the containter:

- the `data` directory is mounted in your locally running container as a read-only directory `/codeexecution/data`
- the `submission` directory is mounted in your locally running container as `/codeexecution/submission`

Your `submission.zip` file must exist in the `submission` folder on your host machine in order to be processed when you are testing execution locally.

Use `make pack-benchmark` to create your submission. It takes a `LANGUAGE` argument that can be either `python` or `R`. The command zips everything in the `benchmark/<LANGUAGE>` folder and saves the zip archive to `submission/submission.zip`. For example, to prepare the example submission and put it into the submission folder, run:

```bash
make pack-benchmark LANGUAGE=python
```

When you run this in the future, you should check and remove any existing `submission/submission.zip` file. The `make pack-benchmark` command does not overwrite this file (so we won't accidentally lose your work).

### Test running your submission locally

You can execute the same containers locally that we will use on the DrivenData platform to ensure your code will run.

Make sure you have the [prerequisites](#prerequisites) installed. Then, you can run the following command within the repository to download the official image:

```bash
make pull
```

### Making a submission

Once you have the container image downloaded locally, you will be able to run it to see if your code works. You can put your `submission.zip` file in the `submission` folder and run the following command (or just use the sample one that was created when you ran `make pack-benchmark` above):

```bash
make test-submission
```

This will spin up the container, mount the local folders as drives within the folder, and follow the same steps that will run on the platform to unpack your submission and run your code  against what it finds in the `/codeexecution/data` folder.

### Reviewing the logs

When you run `make test-submission` the logs will be printed to the terminal. They will also be written to the `submission` folder as `log.txt`. You can always review that file and copy any versions of it that you want from the `submission` folder. The errors there will help you to determine what changes you need to make so your code executes successfully.

## (2) Updating the runtime packages

We accept contributions to add dependencies to the runtime environment. To do so, follow these steps:

1. Fork this repository
2. Make your changes
3. Test them and commit using git
3. Open a pull request to this repository

If you're new to the GitHub contribution workflow, check out [this guide by GitHub](https://guides.github.com/activities/forking/).

### Adding new Python packages

We use [conda](https://docs.conda.io/en/latest/) to manage Python dependencies. Add your new dependencies to both `runtime/py-cpu.yml` and `runtime/py-gpu.yml`. Please also add your dependencies to `runtime/tests/test-installs.py`, below the line `## ADD ADDITIONAL REQUIREMENTS BELOW HERE ##`.

Your new dependency should follow the format in the yml and be pinned to a particular version of the package and build with conda.

### Testing new dependencies

Please test your new dependency locally by recreating the relevant conda environment using the appropriate CPU or GPU `.yml` file. Try activating that environment and loading your new dependency.

Once that works, you'll want to make sure it works within the container as well. To do so, you can run:

```
make test-container
```

Note: this will run `make build` to create the new container image with your changes automatically, but you could also do it manually.

This will build a local version of the official container and then run the import tests to make sure the relevant libraries can all be successfully loaded. This must pass before you submit a pull request to our repo to update the requirements. If it does not, you'll want to figure out what else you need to make the dependencies happy.

If you have problems, the following command will run a bash shell in the container to let you interact with it. Make sure to activate the `conda` environment (e.g., `conda activate py-cpu`) when you start the container if you want to test the dependencies!

```
make debug-container
```

### Opening a pull request

After making and testing your changes, commit your changes and push to your fork. Then, when viewing the repository on github.com, you will see a banner that lets you open the pull request. For more detailed instructions, check out [GitHub's help page](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).

Once you open the pull request, Github Actions will automatically try building the Docker images with your changes and run the tests in `runtime/tests`. These tests take ~30 minutes to run through, and may take longer if your build is queued behind others. You will see a section on the pull request page that shows the status of the tests and links to the logs.

You may be asked to submit revisions to your pull request if the tests fail, or if a DrivenData team member asks for revisions. Pull requests won't be merged until all tests pass and the team has reviewed and approved the changes.

---

## Happy modeling!

Thanks for reading! Enjoy the competition, and [hit up the forums](https://community.drivendata.org/) if you have any questions!
