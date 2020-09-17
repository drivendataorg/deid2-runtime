FROM continuumio/miniconda:4.7.12

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y \
        build-essential \
        git \
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

COPY py-cpu.yml r-cpu.yml package-installs-cpu.R /envs/

# Create Python environment
RUN conda update conda -y && \
    conda env create -f /envs/py-cpu.yml && \
    conda clean -a -y

# Create R environment
RUN conda update conda -y && \
    conda env create -f /envs/r-cpu.yml && \
    conda clean -a -y && \
    conda clean -f -y && \
    /opt/conda/envs/r-cpu/bin/R -f /envs/package-installs-cpu.R

# Execute the entrypoint.sh script inside the container when we do docker run
CMD ["/bin/bash", "/codeexecution/entrypoint.sh"]
