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
echo "Create a radiolab_docker container."
echo ""
echo "Usage: ./create.sh -p [data_path] -l [freesurfer_license] -r [runtime]"
echo "-r, --runtime        Specify the RUNTIME, either "normal" or "nvidia". (default: normal)"
echo "-p, --data-path      Specify the "data_path" to be mounted to /DATA in inside the container."
echo "                         Note, the "data_path" should be a DIR,"
echo "                         and you are supposed to own the rwx permissions to it."
echo "-n, --name           Specify the service name of the container. (default: radiolab_docker)"
echo "-b, --binding-port   Specify the local port for jupyter-notebook. (default: 8888)"
echo "-l, --fs-license     Specify the Freesurfer license for a full functional Freesurfer."
echo ""
}

# Read arguments
for arg in "$@"; do
  shift
  case "$arg" in
    "--runtime")      set -- "$@" "-r" ;;
    "--data-path")    set -- "$@" "-p" ;;
    "--fs-license")   set -- "$@" "-l" ;;
    "--name")         set -- "$@" "-n" ;;
    "--binding-port") set -- "$@" "-b" ;;
    "--help")         set -- "$@" "-h" ;;
    *)                set -- "$@" "$arg"
  esac
done

# Get runtime option
while getopts "r:p:l:n:b:h" opt
do
    case ${opt} in
    r)
        RUNTIME=${OPTARG}
        ;;
    p)
        DATA_PATH_OG=${OPTARG}
        ;;
    l)
        FS_LICENSE_OG=${OPTARG}
        ;;
    n)
        RADIOLABDOCKER_NAME=${OPTARG}
        ;;
    b)
        PORT=${OPTARG}
        ;;
    h)
        Usage
        exit 1
        ;;
    esac
done

IMAGE_init="radiolab_docker"

if [[ -z ${RADIOLABDOCKER_NAME} ]]; then
    RADIOLABDOCKER_NAME="radiolab_docker"
fi

if [[ -z ${PORT} ]]; then
    PORT="8888"
fi

if [[ -z ${RUNTIME} ]]; then
    echo -e "${WARNING}: Runtime has not been specified, default is normal"
    RUNTIME=normal
fi

IMAGE=${IMAGE_init}_${RUNTIME}

if [[ -z `echo "normal nvidia" | tr ' ' '\n' | grep -F -w ${RUNTIME}` ]]; then
    echo -e "${ERROR}: Invalid runtime!"
    Usage
    exit 1
fi

NV_RUNTIME=`docker run -it --rm ${IMAGE}:latest bash -c 'echo $NV_RUNTIME' | sed -e "s/\r//g"`
if [[ ${NV_RUNTIME} == "1" ]]; then
    NV_RUNTIME="nvidia"
elif [[ ${NV_RUNTIME} == "0" ]]; then
    NV_RUNTIME="normal"
fi

if [[ ${NV_RUNTIME} != ${RUNTIME} ]]; then
    echo -e "The runtime you provided is ${hint}${RUNTIME}${normal}, while it shows the ${hint}${IMAGE}${normal} is ${hint}${NV_RUNTIME}${normal} runtime."
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

./build.sh -c -r ${RUNTIME}


# Check os type
case "$OSTYPE" in
    linux*)   OS="UNIX" ;;
    msys*)    OS="WINDOWS" ;;
    *)        OS="unknown: $OSTYPE" ;;
esac

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
                EXIST_DOCKER=( `docker ps -a | awk -F '   ' '{print $NF}'` )
                if [[ ! ${EXIST_DOCKER[@]:1} =~ ${RADIOLABDOCKER_NAME} ]]; then
                    RUNNING_DOCKER=( `docker ps -a | awk -F '   ' '{print $NF":"$5}' | awk '{print $1}'` )
                    if [[ ${RUNNING_DOCKER[*]:1} =~ ${RADIOLABDOCKER_NAME}:Up ]]; then
                    if [[ ! -z ${RUNNING_COMPOSE} ]]; then
                        echo -e "${WARNING}: We found existing \"${hint}${RADIOLABDOCKER_NAME}${normal},\" and it's ${hint}RUNNING${normal}!"
                        echo -e "${WARNING}: This process intents to ${hint}STOP ALL THE RUNNING PROCESSES${normal} in the current \"${hint}${RADIOLABDOCKER_NAME}${normal}\" instence and ${hint}RE-CREATE${normal} it."
                    else
                        echo -e "${WARNING}: We found existing \"${hint}${RADIOLABDOCKER_NAME}${normal}.\""
                        echo -e "${WARNING}: This process intents to ${hint}RE-CREATE${normal} it."
                    fi
                    echo -e "${WARNING}: Also note, the \"${hint}/DATA${normal}\" (container) will redirect to \"${hint}${DATA_PATH}${normal}\" (host). "
                fi
                echo -e "${PROCEED}: Creating ${RADIOLABDOCKER_NAME}"
                if [[ -z ${FS_LICENSE_OG} ]]; then
                    echo -e "${WARNING}: No freesurfer license was supplied, thus the freesurfer will not work properly."
                    sed -i -e "/\s\+-\s\_FS_LICENSE.\+/{s/#//g;s/\(\s\+-\s\_FS_LICENSE.\+\)/#\1/g}" build/tmp/docker-compose.yml
                else
                    FS_LICENSE=`readlink -e ${FS_LICENSE_OG}`
                    if [[ -z ${FS_LICENSE} || -d ${FS_LICENSE} ]]; then
                        echo -e "${ERROR}: The path \"${hint}${FS_LICENSE}${normal}\" is invalid for a freesurfer license file!"
                        exit 1
                    else
                        echo -e "${INFORM}: Freesurfer license is supplied."
                        sed -i -e "/\s\+-\s\_FS_LICENSE.\+/{s/#//g}" build/tmp/docker-compose.yml
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
 		USER_name=`whoami`
 		CURRENT_ID=`id -u`:`id -g`
                HOME_local=`echo ${HOME} | sed "s:/:\\\\\/:g"`
 		HOME_docker=`echo /home/${USER_name} | sed "s:/:\\\\\/:g"`
 		DATA=`echo ${DATA_PATH} | sed "s:/:\\\\\/:g"`
 		FS_LICENSE=`echo ${FS_LICENSE} | sed "s:/:\\\\\/:g"`

		if [[ ! -d build/tmp/ ]]; then
			mkdir -p build/tmp
		fi
		if [[ ! -d build/tmp/${RADIOLABDOCKER_NAME} ]]; then
			mkdir -p build/tmp/${RADIOLABDOCKER_NAME}
		fi

		echo "${USER_name}:x:${CURRENT_ID}:${USER_name}:${HOME_docker}:/bin/bash" > ./build/tmp/passwd
		echo "${USER_name}:x:`id -g`" > ./build/tmp/group

		sed -e 's/_RADIOLAB_DOCKER/'"$RADIOLABDOCKER_NAME"'/g' \
            -e 's/_IMAGE/'"$IMAGE"'/g' \
		    -e 's/_HOME_local/'"$HOME_local"'/g' \
		    -e 's/_HOME_docker/'"$HOME_docker"'/g' \
		    -e 's/_USER/'"$USER_name"'/g' \
		    -e 's/_CURRENT_ID/'"$CURRENT_ID"'/g' \
		    -e 's/_PORT/'"$PORT"'/g' \
		    -e 's/_DATA/'"$DATA"'/g' \
		    -e 's/_FS_LICENSE/'"$FS_LICENSE"'/g' \
		    ./build/tmp/docker-compose.yml > build/tmp/${RADIOLABDOCKER_NAME}/docker-compose.yml

        # Fix $DISPLAY binding depends on $OSTYPE
        if [[ ${OS} == "UNIX" ]]; then
            sed -i -e 's/host.docker.internal//g' build/tmp/${RADIOLABDOCKER_NAME}/docker-compose.yml
        fi

		docker-compose -f build/tmp/${RADIOLABDOCKER_NAME}/docker-compose.yml up -d --force-recreate
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