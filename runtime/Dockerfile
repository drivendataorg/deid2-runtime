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

COPY ./entrypoint.sh /codeexecution/entrypoint.sh
RUN chmod +x /codeexecution/entrypoint.sh

USER 1000

# install miniconda as system python
COPY ./Miniconda3-py37_4.8.3-Linux-x86_64.sh /opt/miniconda.sh 
RUN /bin/bash /opt/miniconda.sh -b -p /opt/conda

ENV PATH /opt/conda/bin:$PATH
COPY ./py-${CPU_OR_GPU}.yml ./r-${CPU_OR_GPU}.yml ./package-installs-${CPU_OR_GPU}.R /envs/

# Create Python environment
RUN conda update conda -y && \
    conda env create -f /envs/py-${CPU_OR_GPU}.yml && \
    conda clean -a -y

# Create R environment
RUN conda update conda -y && \
    conda env create -f /envs/r-cpu.yml && \
    conda clean -a -y && \
    conda clean -f -y && \
    /opt/conda/envs/r-${CPU_OR_GPU}/bin/R -f /envs/package-installs-${CPU_OR_GPU}.R

# Execute the entrypoint.sh script inside the container when we do docker run
CMD ["/bin/bash", "/codeexecution/entrypoint.sh"]
