#!/bin/bash

# Set colors
normal="\033[0m"
error="\033[41;33m"
warning="\033[43;31m"
proceed="\033[42;30m"
inform="\033[46;30m"
hint="\033[4;36m"
ERROR="${error}ERROR${normal}"
WARNING="${warning}WARNING${normal}"
PROCEED="${proceed}PROCEEDING${normal}"
INFORM="${inform}INFORM${normal}"

Usage () {
echo ""
echo "Run "radiolab_docker" container."
echo "then build the Docker image from the begining."
echo ""
echo "Usage: ./run.sh [options]"
echo "-n, --container-name   Specify the container name. (default: radiolab_dock)"
echo "-h, --help           Show this message."
echo ""
}

for arg in "$@"; do
  shift
  case "$arg" in
    "--container-name") set -- "$@" "-n" ;;
    "--help")           set -- "$@" "-h" ;;
    *)                  set -- "$@" "$arg"
  esac
done

# Get fsl parallelism
while getopts "n:h" opt
do
    case ${opt} in
    n)
        CONTAINER=${OPTARG}
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

# Check os type
case "$OSTYPE" in
    linux*)   OS="UNIX" ;;
    msys*)    OS="WINDOWS" ;;
    *)        OS="unknown: $OSTYPE" ;;
esac

if [[ -z ${CONTAINER} ]]; then
    CONTAINER="radiolab_docker"
fi

EXIST_DOCKER=( `docker ps -a | awk -F '   ' '{print $NF}'` )
if [[ ! ${EXIST_DOCKER[@]:1} =~ ${CONTAINER} ]]; then
    echo -e "${ERROR}: \"${hint}${CONTAINER}${normal}\" dose not exist. Please run ${hint}create.sh${normal} first."
    exit 1
else
    RUNNING_DOCKER=( `docker ps -a | awk -F '   ' '{print $NF":"$5}' | awk '{print $1}'` )
    if [[ ${RUNNING_DOCKER[*]:1} =~ ${CONTAINER}:Up ]]; then
        echo -e "${PROCEED}: \"${hint}${CONTAINER}${normal}\" is RUNNING."
    else
        echo -e "${PROCEED}: \"${hint}${CONTAINER}${normal}\" is not RUNNING, bringing the container up online."
        docker container start ${CONTAINER} > /dev/null 2>&1
    fi

    check_xhost="$(command -V xhost 2> /dev/null)"
    if [[ ${check_xhost} ]]; then
	    echo -e "${PROCEED}: Disable access control of the X server."
	    `xhost +` > /dev/null 2>&1 &
    else
	    echo -e "${WARNING}: \"${hint}xhost${normal}\" command is not found! Please disable the access control of X server manually to insure the gui app display."
    fi


    if [[ ${OS} != "UNIX" ]]; then
        winptyapply=winpty
    fi

    echo -e "${PROCEED}: Entering interactive shell."
    ${winptyapply} docker exec -it ${CONTAINER} bash -c "source /radiolabdocker/startup.sh"
fi
