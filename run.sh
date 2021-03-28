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

EXIST_DOCKER=`docker ps -a | grep radiolab_docker | awk '{print $NF}'`
if [[ -z ${EXIST_DOCKER} ]]; then
    echo -e "${ERROR}: \"${hint}radiolab_docker${normal}\" dose not exist. Please run ${hint}create.sh${normal} first."
    exit 1
else
    RUNNING_DOCKER=`docker ps -a | grep radiolab_docker | awk -F '   ' '{print $5}' | grep Up`
    if [[ ! -z ${RUNNING_DOCKER} ]]; then
        echo -e "${PROCEED}: \"${hint}radiolab_docker${normal}\" is RUNNING."
    else
        echo -e "${PROCEED}: \"${hint}radiolab_docker${normal}\" is not RUNNING, bringing the container up online."
        docker container start radiolab_docker > /dev/null 2>&1
    fi
    echo -e "${PROCEED}: Entering interactive shell."
    docker exec -it radiolab_docker bash
fi



