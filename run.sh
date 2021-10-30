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
echo "Run "${hint}radiolab_docker${normal}" container."
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
echo "-n, --container-name   Specify the container name. (default: radiolab_dock)"
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./run.sh             Enter the interactive shell with \$FSLPARALLEL=\$(echo "\$\(nproc\)-2" | bc),"
echo "                       which means number of threads for fsl_sub will set to maximum num of cores - 2 (n - 2)"
echo "./run.sh -p 6        Enter the interactive shell with \$FSLPARALLEL=6,"
echo "                       which means fsl_sub will run in 6 threads"
echo ""
}

for arg in "$@"; do
  shift
  case "$arg" in
    "--fsl-parallel")   set -- "$@" "-p" ;;
    "--container-name") set -- "$@" "-n" ;;
    "--help")           set -- "$@" "-h" ;;
    *)                  set -- "$@" "$arg"
  esac
done

# Get fsl parallelism
while getopts "p:n:h" opt
do
    case ${opt} in
    p)
        FSL_PARA=${OPTARG}
        ;;
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

if [[ ! -z ${FSL_PARA} ]]; then
    check_fslsub_num=`test -n "${FSL_PARA}" && test -z ${FSL_PARA//[0-9]} && echo 1 || echo 0`
    if [[ ${check_fslsub_num} != "1" ]];then
       echo -e "${ERROR}: -p, --fsl-parallel needs to be supplied with a positive integer number."
       exit 1
    fi
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
    if [[ -z ${FSL_PARA} ]]; then
        echo -e "${INFORM}: Number of threads for fsl_sub will set to maximum num of cores - 2 (n - 2) by default."
        echo -e "${INFORM}: You can set ${hint}\$FSLPARALLEL${normal} inside the shell to control its behavior."
        ${winptyapply} docker exec -it ${CONTAINER} bash -c 'export FSLPARALLEL=$(echo "$(nproc)-2" | bc) && source /radiolabdocker/startup.sh'
    else
        if [[ ${FSL_PARA} == 0 ]]; then
            echo -e "${INFORM}: Multi-threads fsl_sub functionality is off."
        elif [[ ${FSL_PARA} == 1 ]]; then
            echo -e "${INFORM}: Multi-threads fsl_sub functionality is on and sets to maximum num of cores that available."
        else
            echo -e "${INFORM}: Multi-threads fsl_sub functionality is on and sets to ${FSL_PARA}."
        fi
        echo -e "${INFORM}: You can set ${hint}\$FSLPARALLEL${normal} inside the shell to control its behavior."
        ${winptyapply} docker exec -it ${CONTAINER} bash -c "export FSLPARALLEL=${FSL_PARA} && source /radiolabdocker/startup.sh"
    fi
fi
