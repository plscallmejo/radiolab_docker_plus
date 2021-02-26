#!/bin/bash

# Get runtime option
while getopts ":r" opt
do
    case ${opt} in
    r)
        RUNTIME=${OPTARG}
        ;;
    esac
done

# Build a basic docker image
mkdir -p build/base
touch build/base/Dockerfile
RUNTIME="intel"
if [[ $RUNTIME = "nvidia" ]]; then
echo '# nvidia/cudagl:9.1-runtime-ubuntu16.04
FROM nvidia/cudagl:9.1-runtime-ubuntu16.04
# nvidia-container-runtime
ENV NV_RUNTIME=TRUE
ENV BASE="nvidia/cudagl:9.1-runtime-ubuntu16.04"
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
RUN sed -i "s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list \
    && echo "deb https://mirrors.aliyun.com/nvidia-cuda/ubuntu1604/x86_64/ ./" > /etc/apt/sources.list.d/cuda.list'  > build/base/Dockerfile
elif [[ $RUNTIME = "intel" ]]; then
echo '#ubuntu:16.04
FROM ubuntu:16.04
# mesa runtime
ENV NV_RUNTIME=FALSE
ENV BASE="ubuntu:16.04"
RUN sed -i "s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           qt5-default \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*' > build/base/Dockerfile
fi

docker build -t radiolab_base:latest build/base

# Build Docker image with proper runtime
docker build -t radiolab:latest build --build-arg RUNTIME=$RUNTIME

