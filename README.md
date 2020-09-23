# NIST De-ID2 Challenge

![Python 3.8](https://img.shields.io/badge/Python-3.8-blue) [![GPU Docker Image](https://img.shields.io/badge/Docker%20image-gpu--latest-green)](https://hub.docker.com/r/drivendata/sfp-competition/tags?page=1&name=gpu-latest) [![CPU Docker Image](https://img.shields.io/badge/Docker%20image-cpu--latest-lightgrey)](https://hub.docker.com/r/drivendata/sfp-competition/tags?page=1&name=cpu-latest) 

Welcome to the runtime repository for the [NIST De-ID2 Challenge](https://www.drivendata.org/competitions/68/competition-differential-privacy-maps-1). This repository contains the definition of the environment where your code submissions will run. It specifies both the operating system and the software packages that will be available to your solution.

This repository has two primary uses for competitors:

 - **Testing your code submission**: It lets you test your `submission.zip` file with a locally running version of the container so you don't have to wait for it to process on the competition site to find programming errors.
 - **Requesting new packages in the official runtime**: It lets you test adding additional packages to the [official runtime environment](runtime/py-gpu.yml). The official runtime uses **Python 3.8**. You can then submit a PR to request compatible packages be included in the official container image.

 ----

### [Getting started](#0-getting-started)
 - [Prerequisites](#prerequisites)
 - [Quickstart](#quickstart)
### [Testing your submission locally](#1-testing-your-submission-locally)
 - [Implement your solution](#implement-your-solution)
 - [Example benchmark submission](#example-benchmark-submission)
 - [Making a submission](#making-a-submission)
 - [Reviewing the logs](#reviewing-the-logs)
### [Updating the runtime packages](#2-updating-the-runtime-packages)
 - [Adding new Python packages](#adding-new-python-package)
 - [Adding new R packages](#adding-new-r-packages)
 - [Testing new dependencies](#testing-new-dependencies)
 - [Opening a pull request](#opening-a-pull-request)

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

To test out the full execution pipeline, run the following commands in order in the terminal. These will get the Docker images, zip up an example submission script, and run the submission on your locally running version of the container.

```
make pull
make pack-benchmark
make test-submission
```

You should see output like this in the end (and find the same logs in the folder `submission/log.txt`):

```
➜ make pack-benchmark
cd benchmark/py; zip -r ../../submission/submission.zip ./*
  adding: main.py (deflated 63%)

➜ make test-submission
chmod -R 0777 submission/
docker run \
        -it \
         \
        --network none \
        --mount type=bind,source=/home/robert/projects/deid2-runtime/data,target=/codeexecution/data,readonly \
        --mount type=bind,source=/home/robert/projects/deid2-runtime/submission,target=/codeexecution/submission \
        --shm-size 8g \
        b09bce29f1c9
GPU unavailable; falling back to CPU.
Unpacking submission...
Archive:  ./submission/submission.zip
  inflating: ./main.py
Running submission with Python
INFO:root:loading parameters
INFO:root:reading submission format from /codeexecution/data/submission_format.csv ...
INFO:root:read dataframe with 10,008 rows
INFO:root:reading raw incident data from /codeexecution/data/incidents.csv ...
INFO:root:read dataframe with 1,455,608 rows
INFO:root:counting up incidents by (neighborhood, year, month)
INFO:root:privatizing each set of 10008 counts...
100%|██████████| 10008/10008 [00:02<00:00, 3555.32it/s]
INFO:root:writing 10,008 rows out to /codeexecution/submission.csv
Exporting submission.csv result...
Script completed its run.
DeprecationWarning: 'source deactivate' is deprecated. Use 'conda deactivate'.
============================= test session starts ==============================
platform linux -- Python 3.8.5, pytest-6.0.2, py-1.9.0, pluggy-0.13.1
rootdir: /codeexecution
collected 6 items

tests/test_submission.py ......                                          [100%]

============================== 6 passed in 0.38s ===============================
INFO:root:reading incidents from /codeexecution/data/incidents.csv ...
/opt/conda/envs/py-cpu/lib/python3.8/site-packages/numpy/lib/arraysetops.py:580: FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
  mask |= (ar1 == a)
INFO:root:reading submission from /codeexecution/submission.csv ...
INFO:root:read dataframe with 10,008 rows
INFO:root:computing ground truth ...
INFO:root:read dataframe with 10,008 rows
INFO:root:OVERALL SCORE: 13.886839292705211
================ END ================
```

Running `make` at the terminal will tell you all the commands available in the repository:

```
➜ make

Settings based on your machine:
CPU_OR_GPU=cpu                  # Whether or not to try to build, download, and run GPU versions
SUBMISSION_IMAGE=b09bce29f1c9   # ID of the image that will be used when running test-submission

Available competition images:
drivendata/deid2-competition:gpu-local (a9ef4bf9be1c); drivendata/deid2-competition:cpu-local (b09bce29f1c9);

Available commands:

build               Builds the container locally, tagging it with cpu-local or gpu-local
debug-container     Start your locally built container and open a bash shell within the running container; same as submission setup except has network access
export-requirements Export the conda environment YAML from the container
pack-benchmark      Creates a submission/submission.zip file from whatever is in the "benchmark" folder
pull                Pulls the official container tagged cpu-latest or gpu-latest from Docker hub
resolve-python-requirements Resolve the Python dependencies inside the container and write out to the host environment YAML file
resolve-r-requirements Resolve the R dependencies inside the container and write out to the host environment YAML file
test-container      Ensures that your locally built container can import all the Python packages successfully when it runs
test-submission     Runs container with submission/submission.zip as your submission and data as the data to work with
unpin-requirements  Remove specific version pins from Python conda environment YAML
```

To find out more about what these commands do, keep reading! :eyes:

## (1) Testing your submission locally

Your submission will run inside a Docker container, a virtual operating system that allows for a consistent software environment across machines. This means that if your submission successfully runs in the container on your local machine, you can be pretty sure it will successfully run when you make an official submission to the DrivenData site.

In Docker parlance, your computer is the "host" that runs the container. The container is isolated from your host machine, with the exception of the following directories:

 - the `data` directory on the host machine is mounted in the container as a read-only directory `/codeexecution/data`
 - the `submission` directory on the host machine is mounted in the container as `/codeexecution/submission`

When you make a submission, the code execution platform will unzip your submission assets to the `/codeexecution` folder. This must result in either a `main.py`, `main.R`, or `main` executable binary in the `/codeexecution`. On the official code execution platform, we will take care of mounting the data―you can assume your submission will have access to `incidents.csv`, `parameters.json`, and `submission_format.csv` in `/codeexecution/data`. You are responsible for creating the submission script that will read from `/codeexecution/data` and write to `/codeexecution/submission.csv`. Keep in mind that your submission will not have access to the internet, so everything it needs to run must be provided in the `submission.zip` you create. (You _are_ permitted to write intermediate files to `/codeexecution/submission`.)

### Implement your solution

In order to test your code submission, you will need a code submission! Implement your solution as either a Python script named `main.py`, an R script named `main.R`, or a binary executable named `main`. Next, create a `submission.zip` file containing your code and model assets.

**NOTE: You will implement all of your training and experiments on your machine. It is highly recommended that you use the same package versions that are in the runtime ([Python (CPU)](runtime/py-cpu.yml), [Python (GPU)](runtime/py-gpu.yml), [R (CPU)](runtime/r-cpu.yml), or [R (GPU)](runtime/r-gpu.yml)). They can be installed with `conda`.**

The [submission format page](https://www.drivendata.org/competitions/68/competition-differential-privacy-maps-1/page/260/#submissions) contains the detailed information you need to prepare your submission.

### Example benchmark submission

We wrote a benchmark in Python to serve as a concrete example of a submission. Use `make pack-benchmark` to create the benchmark submission from the source code. The command zips everything in the `benchmark` folder and saves the zip archive to `submission/submission.zip`. To prevent losing your work, this command will not overwrite an existing submission. To generate a new submission, you will first need to remove the existing `submission/submission.zip`.

### Making a submission

Make sure you have the [prerequisites](#prerequisites) installed. Then, run the following command to download the official image:

```bash
make pull
```

Now after you have packed up your solution in `submission/submission.zip` (or generated the sample submission with `make pack-benchmark`), you can test it locally by running:

```bash
make test-submission
```

This will start the container, mount the local data and submission folders as folders within the container, and follow the same steps that will run on the platform to unpack your submission and run your code.

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

### Adding new R packages

We prefer to use conda to manage R dependencies. Take a look at what packages are available from [Anaconda's `pkgs/r`](https://repo.anaconda.com/pkgs/r/) and from [`conda-forge`](https://conda-forge.org/feedstocks/). Note that R packages in conda typically start with the prefix `r-`. Add your new dependencies to both `runtime/r-cpu.yml` and `runtime/r-gpu.yml`.

If your dependencies are not available from the Anaconda or `conda-forge`, you can also add installation code to both the install scripts `runtime/package-installs-cpu.R` and `runtime/package-installs-gpu.R` to install from CRAN or GitHub.

Please also add your dependencies to `runtime/tests/test-installs.R`, below the line `## ADD ADDITIONAL REQUIREMENTS BELOW HERE ##`.

### Testing new dependencies

Test your new dependency locally by recreating the relevant conda environment using the appropriate CPU or GPU `.yml` file. Try activating that environment and loading your new dependency. Once that works, you'll want to make sure it works within the container as well. To do so, you can run:

```
make test-container
```

Note: this will run `make build` to create the new container image with your changes automatically, but you could also do it manually.

This will build a local version of the container and then run the import tests to make sure the relevant libraries can all be successfully loaded. This must pass before you submit a pull request to this repository to update the requirements. If it does not, you'll want to figure out what else you need to make the dependencies happy.

If you have problems, the following command will run a bash shell in the container to let you interact with it. Make sure to activate the `conda` environment (e.g., `source activate py-cpu`) when you start the container if you want to test the dependencies!

```
make debug-container
```

### Opening a pull request

After making and testing your changes, commit your changes and push to your fork. Then, when viewing the repository on github.com, you will see a banner that lets you open the pull request. For more detailed instructions, check out [GitHub's help page](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).

Once you open the pull request, Github Actions will automatically try building the Docker images with your changes and run the tests in `runtime/tests`. These tests take ~30 minutes to run through, and may take longer if your build is queued behind others. You will see a section on the pull request page that shows the status of the tests and links to the logs.

You may be asked to submit revisions to your pull request if the tests fail, or if a DrivenData team member asks for revisions. Pull requests won't be merged until all tests pass and the team has reviewed and approved the changes.

---

## Good luck; have fun!

Thanks for reading! Enjoy the competition, and [hit up the forums](https://community.drivendata.org/) if you have any questions!
