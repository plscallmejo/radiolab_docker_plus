#!/bin/bash

# Set colors
normal="\033[0m"
error="\033[41;33m"
warning="\033[43;31m"
proceed="\033[42;30m"
hint="\033[4;36m"
ERROR="${error}ERROR${normal}"
WARNING="${warning}WARNING${normal}"
PROCEED="${proceed}PROCEEDING${normal}"

# Get runtime option
while getopts "r:" opt
do
    case ${opt} in
    r)
        RUNTIME=${OPTARG}
        ;;
    \?)
        echo -e "${ERROR}: Invalid option."
        exit 1
        ;;
    esac
done

# Setting a basic docker image
mkdir -p build/base
touch build/base/Dockerfile
if [[ ! -n ${RUNTIME} ]]; then
    echo -e "${WARNING}: no ${hint}-r${normal} (RUNTIME) option was supplied, so automatically setting to \"${hint}intel${normal}\""
    RUNTIME="intel"
fi
if [[ ${RUNTIME} = "nvidia" ]]; then
echo -e "${PROCEED}: Building base image from \"${hint}nvidia/cudagl:9.1-runtime-ubuntu16.04${normal}\ with \"${hint}nvidia runtime${normal}\" support"
echo '# nvidia/cudagl:9.1-runtime-ubuntu16.04
FROM nvidia/cudagl:9.1-runtime-ubuntu16.04
# nvidia-container-runtime
ENV NV_RUNTIME=TRUE
ENV BASE="nvidia/cudagl:9.1-runtime-ubuntu16.04"
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
RUN sed -i "s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list \
    && echo "deb https://mirrors.aliyun.com/nvidia-cuda/ubuntu1604/x86_64/ ./" > /etc/apt/sources.list.d/cuda.list'  > build/base/Dockerfile
elif [[ ${RUNTIME} = "intel" ]]; then
echo -e "${PROCEED}: Building base image from \"${hint}ubuntu:16.04${normal}\""
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
else
echo -e "${ERROR}: ${hint}-r${normal} (RUNTIME) option can only be either \"${hint}intel${normal}\" or \"${hint}nvidia${normal}\""
exit 1
fi

## Build base image
docker build -t radiolab_base:latest build/base
echo -e "${PROCEED}: Base image build complete"

# Build Docker image with proper runtime
echo -e "${PROCEED}: Build \"${hint}radiolab${normal}\" image from base"
docker build -t radiolab:latest build --build-arg RUNTIME=$RUNTIME

