FROM nvidia/cuda:11.0-base-ubuntu20.04

# non-interactive package installs by setting these up front
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV TZ=UTC
ARG DEBIAN_FRONTEND=noninteractive

ARG CPU_OR_GPU=gpu

RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y \
        build-essential \
        git \
        libglu1-mesa \
        pkg-config \
        software-properties-common \
        unzip \
        wget && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/src/*

# Limited user
RUN groupadd -g 999 appuser && \
    useradd -r -u 1000 -g appuser appuser

RUN mkdir /envs /home/appuser /codeexecution && \
    chown -R appuser /opt /envs /home/appuser /codeexecution

# install miniconda as system python
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh -O /opt/miniconda.sh && \
	/bin/bash /opt/miniconda.sh -b -p /opt/conda

ENV PATH /opt/conda/bin:$PATH

# Create Python environment
COPY ./py-${CPU_OR_GPU}.yml /envs/
RUN conda update conda -y && \
    conda env create -f /envs/py-${CPU_OR_GPU}.yml && \
    conda clean -a -y

# Create R environment
COPY ./r-${CPU_OR_GPU}.yml ./package-installs-${CPU_OR_GPU}.R /envs/
RUN conda update conda -y && \
    conda env create -f /envs/r-${CPU_OR_GPU}.yml && \
    conda clean -a -y && \
    conda clean -f -y && \
    /opt/conda/envs/r-${CPU_OR_GPU}/bin/R -f /envs/package-installs-${CPU_OR_GPU}.R

COPY ./entrypoint.sh /codeexecution/entrypoint.sh
RUN chmod +x /codeexecution/entrypoint.sh

COPY ./tests/test_submission.py /codeexecution/tests/test_submission.py
COPY ./scripts/metric.py ./scripts/score.py ./scripts/create_ground_truth.py /codeexecution/

USER 1000

# Execute the entrypoint.sh script inside the container when we do docker run
CMD ["/bin/bash", "/codeexecution/entrypoint.sh"]
