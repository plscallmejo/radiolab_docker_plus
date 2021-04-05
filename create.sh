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

Usage () {
echo ""
echo "Create a radiolab_docker."
echo ""
echo "Usage: ./create.sh [data_path] [freesufer_license]"
echo ""
echo "Specify the "data_path" to be mounted to /DATA in inside the container."
echo "Note, the "data_path" should be a DIR,"
echo "      and you are supposed to own the rwx permissions to it."
echo ""
echo "EXAMPLES:"
echo "./create.sh /the/path/to/your/data"
echo ""
}

DATA_PATH_OG=$1
FS_LICENSE_OG=$2

# Set Data_path
if [[ -z ${DATA_PATH_OG} ]]; then
    echo -e "${ERROR}: Please specify the data path!"
    Usage
    exit 1
else
    DATA_PATH=`readlink -e ${DATA_PATH_OG}`
    if [[ -z ${DATA_PATH} ]]; then
        echo -e "${ERROR}: The data path \"${hint}${DATA_PATH_OG}${normal}\" is invalid! Please check again!"
        Usage
        exit 1
    else
        if [[ -d ${DATA_PATH} ]]; then
            if [[ -r ${DATA_PATH} && -w ${DATA_PATH} && -x ${DATA_PATH} ]]; then
                EXIST_DOCKER=`docker ps -a | grep radiolab_docker | awk '{print $NF}'`
                if [[ ! -z ${EXIST_DOCKER} ]]; then
                    RUNNING_DOCKER=`docker ps -a | grep radiolab_docker | awk -F '   ' '{print $5}' | grep Up`
                    if [[ ! -z ${RUNNING_DOCKER} ]]; then
                        echo -e "${WARNING}: We found existing \"${hint}radiolab_docker${normal},\" and it's ${hint}RUNNING${normal}!"
                        echo -e "${WARNING}: This process intents to ${hint}STOP ALL THE RUNNING PROCESSES${normal} in the current \"${hint}radiolab_docker${normal}\" instence and ${hint}RE-CREATE${normal} it."
                    else
                        echo -e "${WARNING}: We found existing \"${hint}radiolab_docker${normal}.\""
                        echo -e "${WARNING}: This process intents to ${hint}RE-CREATE${normal} it."
                    fi
                    echo -e "${WARNING}: Also note, the \"${hint}/DATA${normal}\" (container) will redirect to \"${hint}${DATA_PATH}${normal}\" (host). "
                    if [[ -z ${FS_LICENSE_OG} ]]; then
                        echo -e "${WARNING}: No freesufer license was supplied, thus the freesufer will not work properly."
                    else
                        FS_LICENSE=`readlink -e ${FS_LICENSE_OG}`
                        if [[ -z ${FS_LICENSE} || -d {FS_LICENSE} ]]; then
                            echo -e "${WARNING}: Also note, The path \"${hint}${FS_LICENSE}${normal}\" is invalid for a freesufer license file!"
                            echo -e "${WARNING}: No freesufer license is supplied, thus the freesufer will not work properly."
                        else
                            echo -e "${PROCEED}: Freesufer license is supplied."
                        fi
                    fi
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
                CURRENT_UID=`id -u`:`id -g` DATA=${DATA_PATH} FS_LICENSE=${FS_LICENSE} docker-compose up -d --force-recreate
            else
                echo -e "${ERROR}: your should own the rwx permissions to the data path \"${hint}${DATA_PATH_OG}${normal}\"! Please check again!"
                Usage
                exit 1
            fi
        else
            echo -e "${ERROR}: The data path \"${hint}${DATA_PATH_OG}${normal}\" should be a DIR or a file! Please check again!"
            Usage
            exit 1
        fi
    fi
fi
