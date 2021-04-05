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

if [[ ! -f docker-compose.yml ]]; then
    echo -e "${ERROR}: Can't find ${hint}docker-compose.yml${normal}."
    echo "Plases run ./build.sh first and specify the runtime flag"
    echo "  to build the radiolab_docker."
    echo "  e.g.  ./build.sh -r nvidia         for nvidia runtime"
    echo "        ./build.sh -r normal         for normal runtime"
    echo "        or ./build.sh"
    echo ""
    echo "If you have pulled the docker image somewhere else,"
    echo "  Please import it, and tag it to radiolab_docker:latest"
    echo "  with the following command:"
    echo ""
    echo "    docker tag <pre-built image> radiolab_docker:latest"
    echo ""
    echo "  then run:"
    echo "        ./build.sh -c -r nvidia     for nvidia runtime"
    echo "        ./build.sh -c -r normal     for normal runtime"
    echo "        or ./build.sh"
    echo ""
    echo "Run ./build.sh -h or ./build.sh --help for more details."
    echo ""
    exit 1
fi

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
                fi
                echo -e "${PROCEED}: Creating radiolab docker"
                if [[ -z ${FS_LICENSE_OG} ]]; then
                    echo -e "${WARNING}: No freesufer license was supplied, thus the freesufer will not work properly."
                    sed  -i -e "/\s\+-\s\$FS_LICENSE.\+/{s/#//g;s/\(\s\+-\s\$FS_LICENSE.\+\)/#\1/g}" docker-compose.yml
                else
                    FS_LICENSE=`readlink -e ${FS_LICENSE_OG}`
                    if [[ -z ${FS_LICENSE} || -d ${FS_LICENSE} ]]; then
                        echo -e "${ERROR}: The path \"${hint}${FS_LICENSE}${normal}\" is invalid for a freesufer license file!"
                        exit 1
                    else
                        echo -e "${INFORM}: Freesufer license is supplied."
                        sed  -i -e "/\s\+-\s\$FS_LICENSE.\+/{s/#//g}" docker-compose.yml
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
