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

usage () {
echo -e " \
******************************** \n \
*** Create a radiolab_docker *** \n \
******************************** \n \
Usage: create_container.sh [data_path] \n \
 [data_path] will be mounted to /DATA in inside the container."

}

# Set Data_path
if [[ -z $1 ]]; then
    echo -e "${ERROR}: Please specify the data path!"
    usage
    exit 1
else
    DATA_PATH=`readlink -e $1`
    if [[ -z ${DATA_PATH} ]]; then
        echo -e "${ERROR}: The data path \"${hint}$1${normal}\" is not valid! Please check again!"
        exit 1
    else
        EXIST_DOCKER=`docker ps -a | grep radiolab_docker | awk '{print $NF}'`
        if [[ ! -z ${EXIST_DOCKER} ]]; then
            RUNNING_DOCKER=`docker ps -a | grep radiolab_docker | awk -F '   ' '{print $5}' | grep Up`
            if [[ ! -z ${RUNNING_DOCKER} ]]; then
                echo -e "${WARNING}: We found existing \"${hint}radiolab_docker${normal},\" and it's ${hint}RUNNING${normal}!"
                echo -e "${WARNING}: This process will intent to ${hint}STOP ALL THE RUNNING PROCESSES${normal} in the current \"${hint}radiolab_docker${normal}\" instence and ${hint}RE-CREATE${normal} it."
            else
                echo -e "${WARNING}: We found existing \"${hint}radiolab_docker${normal}.\""
                echo -e "${WARNING}: This process will intent to ${hint}RE-CREATE${normal} it."
            fi
            echo -e "${WARNING}: Also note, the \"${hint}/DATA${normal}\" (container) will redirect to \"${hint}${DATA_PATH}${normal}\" (host). "
            read -r -p "Comfirm? [Y/N] " input
            case $input in
                [yY][eE][sS]|[yY])
                    SEL="Y"
                    ;;
                [nN][oO]|[nN])
                    SEL="N"
                    ;;
                *)
                    echo "Invalid input..."
                    exit 1
                    ;;
            esac
            if [[ ${SEL} == "N" ]]; then
                exit 1
            fi
        fi
        echo -e "${PROCEED}: Creating radiolab docker"
        CURRENT_UID=`id -u`:`id -g` DATA=${DATA_PATH} docker-compose up -d --force-recreate
    fi
fi
