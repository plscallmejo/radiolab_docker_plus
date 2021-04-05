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

# Usage
Usage () {
echo ""
echo "Build the basic Dockerfile and docker-docker-compose.yml,"
echo "then build the Docker image from the begining."
echo ""
echo "Usage: ./build.sh [options]"
echo "-r, --runtime        Specify the RUNTIME, either "normal" or "nvidia" (default: normal)"
echo "-c, --make-compose   Flag to make the docker-compose.yml file only, no argument is needed."
echo "                     No Docker image will be built."
echo "                     For making or upating docker-compose.yml."
echo "                     e.g. you have pulled the image from somewhere else,"
echo "                         or you already have the image built, and don't want to re-build the image."
echo "                     Note, the pre-built image should tag with "radiolab_docker:latest"."
echo "                       You can use the following command:"
echo "                         "docker tag \<pre-built image\> radiolab_docker:latest""
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./build.sh -r nvidia       will build the Docker image using nvidia RUNTIME."
echo "./build.sh -r nvidia -c    will make the docker-compose.yml file with nvidia RUNTIME only,"
echo "                           but won't build the Docker image."
echo "./build.sh -r normal       will build the Docker image with normal RUNTIME."
echo "./build.sh -c              will make the docker-compose.yml file with normal RUNTIME only,"
echo "                           but won't build the Docker image."
echo ""
}

for arg in "$@"; do
  shift
  case "$arg" in
    "--runtime")      set -- "$@" "-p" ;;
    "--make-compose") set -- "$@" "-c" ;;
    "--help")         set -- "$@" "-h" ;;
    *)                set -- "$@" "$arg"
  esac
done

# Get runtime option
while getopts "r:ch" opt
do
    case ${opt} in
    r)
        RUNTIME=${OPTARG}
        ;;
    c)
        COMPOSE="Y"
        ;;
    h)
        Usage
        exit 1
        ;;
    \?)
        echo -e "${ERROR}: Invalid option."
        Usage
        exit 1
        ;;
    esac
done

# Setting a basic docker image
if [[ ! -n ${RUNTIME} ]]; then
    echo -e "${WARNING}: no ${hint}-r${normal} (RUNTIME) option was supplied, so automatically setting to \"${hint}normal${normal}\" Runtime."
    RUNTIME="normal"
fi
if [[ ${RUNTIME} = "nvidia" ]]; then
if [[ -z ${COMPOSE} ]]; then
mkdir -p build/base
touch build/base/Dockerfile
echo -e "${PROCEED}: Generating base ${hint}Dockerfile${normal}"
echo -e "${PROCEED}: Building base image from \"${hint}nvidia/cudagl:9.1-runtime-ubuntu16.04${normal} with \"${hint}nvidia runtime${normal}\" support"
echo '# nvidia/cudagl:9.1-runtime-ubuntu16.04
FROM nvidia/cudagl:9.1-runtime-ubuntu16.04
# nvidia-container-runtime
ENV NV_RUNTIME=TRUE
ENV BASE="nvidia/cudagl:9.1-runtime-ubuntu16.04"
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
RUN sed -i "s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list \
    && echo "deb https://mirrors.aliyun.com/nvidia-cuda/ubuntu1604/x86_64/ ./" > /etc/apt/sources.list.d/cuda.list'  > build/base/Dockerfile
fi
echo -e "${PROCEED}: Generating ${hint}docker-compose.yml${normal}"
echo '# docker-compose.yml that uses nvidia runtime
version: "2.3"
services:
    radiolab_flow:
        image: radiolab:latest
        runtime: nvidia
        user: $CURRENT_UID
        working_dir: /DATA
        container_name: radiolab_docker
        stdin_open: true
        environment:
            - NVIDIA_VISIBLE_DEVICES=all
            - DISPLAY=$DISPLAY
            - USER=$USER
        volumes:
            - $HOME:$HOME
            - $DATA:/DATA
            - $FS_LICENSE:/opt/freesufer/license.txt
            - /tmp/.X11-unix:/tmp/.X11-unix:rw
            - /etc/group:/etc/group:ro
            - /etc/passwd:/etc/passwd:ro
            - /etc/shadow:/etc/shadow:ro
        tty: true' > docker-compose.yml
elif [[ ${RUNTIME} = "normal" ]]; then
if [[ -z ${COMPOSE} ]]; then
mkdir -p build/base
touch build/base/Dockerfile
echo -e "${PROCEED}: Generating base ${hint}Dockerfile${normal}"
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
fi
echo -e "${PROCEED}: Generating ${hint}docker-compose.yml${normal}"
echo '# docker-compose.yml that use normal
version: "2.3"
services:
    radiolab_flow:
        image: radiolab:latest
        user: $CURRENT_UID
        working_dir: /DATA
        container_name: radiolab_docker
        stdin_open: true
        environment:
            - DISPLAY=$DISPLAY
            - USER=$USER
        volumes:
            - $HOME:$HOME
            - $DATA:/DATA
            - $FS_LICENSE:/opt/freesufer/license.txt
            - /tmp/.X11-unix:/tmp/.X11-unix:rw
            - /etc/group:/etc/group:ro
            - /etc/passwd:/etc/passwd:ro
            - /etc/shadow:/etc/shadow:ro
        tty: true' > docker-compose.yml
else
echo -e "${ERROR}: ${hint}-r${normal} (RUNTIME) option can only be either \"${hint}normal${normal}\" or \"${hint}nvidia${normal}\""
Usage
exit 1
fi

if [[ -z ${COMPOSE} ]]; then
## Build base image
docker build -t radiolab_base:latest build/base
echo -e "${PROCEED}: Base image build complete"

# Build Docker image with proper runtime
echo -e "${PROCEED}: Build \"${hint}radiolab${normal}\" image from base"
docker build -t radiolab:latest build --build-arg RUNTIME=$RUNTIME
fi
