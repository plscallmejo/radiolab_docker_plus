#!/bin/bash

# Set colors
normal="\033[0m"
error="\033[41;33m"
proceed="\033[42;30m"
inform="\033[46;30m"
hint="\033[4;36m"
ERROR="${error}ERROR${normal}"
PROCEED="${proceed}PROCEEDING${normal}"
INFORM="${inform}INFORM${normal}"

Usage () {
echo ""
echo "Build the basic Dockerfile and docker-docker-compose.yml,"
echo "then build the Docker image from the begining."
echo ""
echo "Usage: ./run.sh [options]"
echo "-p, --fsl-parallel   Flag to specify the num of threads for fsl_sub."
echo "                       0 -- off"
echo "                       1 -- on, maximum num of cores available"
echo "                       Or any num < maximum of cores"
echo "                       Note, left it unflag to a default setting"
echo "                          number of threads for fsl_sub will set to "
echo "                          maximum num of cores - 2 (n - 2)"
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./run.sh             Enter the interactive shell with \$FSLPARALLEL=\$(echo "\$\(nproc\)-2" | bc),"
echo "                       which means number of threads for fsl_sub will set to maximum num of cores - 2 (n - 2)"
echo "./run.sh -p 6        Enter the interactive shell with \$FSLPARALLEL=6,"
echo "                       which means fsl_sub will run in 6 threads"
}

for arg in "$@"; do
  shift
  case "$arg" in
    "--fsl-parallel") set -- "$@" "-p" ;;
    "--help") set -- "$@" "-h" ;;
    *)        set -- "$@" "$arg"
  esac
done

# Get fsl parallelism
while getopts "p:h" opt
do
    case ${opt} in
    p)
        FSL_PARA=${OPTARG}
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

if [[ ! -z ${FSL_PARA} ]]; then
    check_fslsub_num=`test -n "${FSL_PARA}" && test -z ${FSL_PARA//[0-9]} && echo 1 || echo 0`
    if [[ ${check_fslsub_num} != "1" ]];then
       echo -e "${ERROR}: -p, --fsl-parallel needs to be supplied with a positive integer number."
       exit 1
    fi
fi

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
    echo -e "${PROCEED}: Disable access control of the X server."
    `xhost +` > /dev/null 2>&1 &
    echo -e "${PROCEED}: Entering interactive shell."
    if [[ -z ${FSL_PARA} ]]; then
        echo -e "${INFORM}: Number of threads for fsl_sub will set to maximum num of cores - 2 (n - 2) by default."
        echo -e "${INFORM}: You can set ${hint}\$FSLPARALLEL${normal} inside the shell to control its behavior."
        docker exec -it radiolab_docker bash -c 'export FSLPARALLEL=$(echo "$(nproc)-2" | bc) && /radiolabdocker/startup.sh'
    else
        if [[ ${FSL_PARA} == 0 ]]; then
            echo -e "${INFORM}: Multi-threads fsl_sub functionality is off."
        elif [[ ${FSL_PARA} == 1 ]]; then
            echo -e "${INFORM}: Multi-threads fsl_sub functionality is on and sets to maximum num of cores that available."
        else
            echo -e "${INFORM}: Multi-threads fsl_sub functionality is on and sets to ${FSL_PARA}."
        fi
        echo -e "${INFORM}: You can set ${hint}\$FSLPARALLEL${normal} inside the shell to control its behavior."
        docker exec -it radiolab_docker bash -c "export FSLPARALLEL=${FSL_PARA} && /radiolabdocker/startup.sh"
    fi
fi
