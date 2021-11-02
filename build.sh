#!/bin/bash

# This is a Building script for radiolab_docker
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

# Usage
Usage () {
echo ""
echo "Build the basic Dockerfiles and docker-compose.yml,"
echo "then build the Docker images from the begining (buildx implement)."
echo ""
echo "Usage: ./build.sh [options]"
echo "-r, --runtime        Specify the RUNTIME, either "normal" or "nvidia". (default: normal)"
echo "-c, --make-compose   Flag to make the docker-compose.yml file only, no argument is needed."
echo "                     No Docker image will be built."
echo "                     For making or upating docker-compose.yml."
echo "                     e.g. you have pulled the image from somewhere else,"
echo "                         or you already have the image built, and don't want to re-build the image."
echo "                     Note, the pre-built image should tag with "radiolab_docker:latest"."
echo "                       You can use the following command:"
echo "                         "docker tag \<pre-built image\> radiolab_docker:latest""
echo "-s, --cn-sp          Use some cn speacialized setting."
echo "                       T for TRUE, and F for FALSE. (default: T)"
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./build.sh -r nvidia       build the Docker image using nvidia runtime."
echo "./build.sh -r nvidia -c    make the docker-compose.yml file with nvidia runtime only,"
echo "                           but won't build the Docker image."
echo "./build.sh -r normal       build the Docker image with normal runtime."
echo "or ./build.sh"
echo "./build.sh -c              make the docker-compose.yml file with normal runtime only,"
echo "                           but won't build the Docker image."
echo ""
}

# CN_procy_control
cn_sp() {
    file=$1
    active=$2

    if [[ -z ${active} ]]; then
        active=0
    fi

    for num in `sed -n -e "/^# CN_SP+/=" ${file}`; do
        line_begin+=`expr $num + 1`
    done

    for num in `sed -n -e "/^# CN_SP-/=" ${file}`; do
        line_end+=`expr $num - 1`
    done

    line_edit=( $( \
        awk -v line_begin=${line_begin[@]} \
        -v line_end=${line_end[@]} \
            'BEGIN {
                split(line_begin, begin, " ");
                split(line_end, end, " ");
                for (i in end) {print begin[i]","end[i]}}' ))

    for lines in ${line_edit[@]};do
        sed -i "${lines}{s/^\#\+//g}" ${file}
    done

        if [[ ${active} -eq 0 ]]; then
            for lines in ${line_edit[@]};do
                sed -i "${lines}{s/^\(.\+\)/#\1/g}" ${file}
            done
        fi
}

# Read arguments
for arg in "$@"; do
  shift
  case "$arg" in
    "--runtime")      set -- "$@" "-r" ;;
    "--make-compose") set -- "$@" "-c" ;;
    "--cn-sp")     set -- "$@" "-s" ;;
    "--help")         set -- "$@" "-h" ;;
    *)                set -- "$@" "$arg"
  esac
done

# Get runtime option
while getopts "r:s:ch" opt
do
    case ${opt} in
    r)
        RUNTIME=${OPTARG}
        ;;
    c)
        COMPOSE="Y"
        ;;
    s)
        CNOPT=${OPTARG}
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

if [[ -n ${CNOPT} ]]; then
    case ${CNOPT} in
        [T])
        CNSWITCH=1
        ;;
        [F])
        CNSWITCH=0
        ;;
        *)
        echo -e "${ERROR}: Invalid option, only ${hint}T${normal} or ${hint}F${normal} can be accepted by the ${hint}-s${normal} flag."
        Usage
        exit 1
        ;;
    esac
fi

# Setting a basic docker image
if [[ -z ${RUNTIME} ]]; then
    echo -e "${WARNING}: no ${hint}-r${normal} (runtime) option was supplied, so automatically setting to \"${hint}normal${normal}\" runtime."
    RUNTIME="normal"
fi

# Check wether cn_sp has speacified
if [[ -z ${CNSWITCH} ]]; then
    CNSWITCH=1
fi

## Generating docker-compose.yml
echo -e "${PROCEED}: Generating ${hint}docker-compose.yml${normal}"
if [[ ! -d build/tmp/ ]]; then
	mkdir -p build/tmp
fi
cp SRC/docker-compose.yml build/tmp/docker-compose.yml

## Generating ./build/tmp/Dockerfile
if [[ ${RUNTIME} = "nvidia" ]]; then
    if [[ -z ${COMPOSE} ]]; then
        mkdir -p build/tmp
        touch build/tmp/Dockerfile_base
        echo -e "${PROCEED}: Generating base ${hint}Dockerfile${normal}"
        echo -e "${PROCEED}: Building base image from \"${hint}nvidia/cuda:11.4.2-cudnn8-runtime-ubuntu20.04${normal} with \"${hint}nvidia runtime${normal}\" support"
        cp SRC/Dockerfile_base_nvidia build/tmp/Dockerfile_base
    fi
elif [[ ${RUNTIME} = "normal" ]]; then
    if [[ -z ${COMPOSE} ]]; then
        mkdir -p build/tmp
        touch build/tmp/Dockerfile_base
        echo -e "${PROCEED}: Generating base ${hint}Dockerfile${normal}"
        echo -e "${PROCEED}: Building base image from \"${hint}ubuntu:20.04${normal}\""
        cp SRC/Dockerfile_base_normal build/tmp/Dockerfile_base
    fi

# Fix docker-compose.yml with according to runtime setting
    echo -e "${PROCEED}: Fixing ${hint}docker-compose.yml${normal} with ${hint}normal${normal} runtime configuration."
    sed  -i -e "/\s\+runtime: nvidia/{s/#//g;s/\(\s\+runtime: nvidia\)/#\1/g}" build/tmp/docker-compose.yml
    sed  -i -e "/\s\+-\sNVIDIA_VISIBLE_DEVICES.\+/{s/#//g;s/\(\s\+-\sNVIDIA_VISIBLE_DEVICES.\+\)/#\1/g}" build/tmp/docker-compose.yml
else
    echo -e "${ERROR}: ${hint}-r${normal} (RUNTIME) option can only be either \"${hint}normal${normal}\" or \"${hint}nvidia${normal}\""
    Usage
    exit 1
fi


# Build the docker images
if [[ -z ${COMPOSE} ]]; then
    ## Copy default Dockerfile
    cp SRC/Dockerfile_OG build/tmp/Dockerfile_OG
    cp SRC/Dockerfile_afni build/tmp/Dockerfile_afni
    cp SRC/Dockerfile_ants build/tmp/Dockerfile_ants
    cp SRC/Dockerfile_fsl build/tmp/Dockerfile_fsl
    cp SRC/Dockerfile_freesurfer build/tmp/Dockerfile_freesurfer
    cp SRC/Dockerfile_dcm2niix build/tmp/Dockerfile_dcm2niix
    cp SRC/Dockerfile_c3d build/tmp/Dockerfile_c3d
    cp SRC/Dockerfile_miniconda build/tmp/Dockerfile_miniconda
    cp SRC/Dockerfile_all build/tmp/Dockerfile_all

    ## CN_SP
    cn_sp build/tmp/Dockerfile_base ${CNSWITCH}

    ## Build base image
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_base:latest -f build/tmp/Dockerfile_base .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_og:latest -f build/tmp/Dockerfile_OG .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_afni:latest -f build/tmp/Dockerfile_afni .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_ants:latest -f build/tmp/Dockerfile_ants .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_fsl:latest -f build/tmp/Dockerfile_fsl .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_freesurfer:latest -f build/tmp/Dockerfile_freesurfer .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_dcm2niix:latest -f build/tmp/Dockerfile_dcm2niix .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_c3d:latest -f build/tmp/Dockerfile_c3d .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 -t radiolab_miniconda:latest -f build/tmp/Dockerfile_miniconda .
    echo -e "${PROCEED}: Base image build complete"

    # Read versioning of the softwares
    AFNI_VERSION=( $(docker run -it --rm radiolab_afni:latest bash -c "afni -version") )
    ANTS_VERSION=( $(docker run -it --rm radiolab_ants:latest bash -c "antsRegistration --version") )
    FSL_VERSION=( $(docker run -it --rm radiolab_fsl:latest bash -c 'echo $FSL_VERSION' | sed -e "s/\r//g") )
    FREESURFER_VERSION=( $(docker run -it --rm radiolab_freesurfer:latest bash -c "freesurfer") )
    DCM2NIIX_VERSION=( $(docker run -it --rm radiolab_dcm2niix:latest bash -c "dcm2niix -v") )
    C3D_VERSION=( $(docker run -it --rm radiolab_dcm2niix:latest bash -c "c3d -version") )

    # Build Docker image with proper runtime
    echo -e "${PROCEED}: Build \"${hint}radiolab${normal}\" image from base."
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 \
            -t radiolab_docker_${RUNTIME}:latest \
            --build-arg SYS_BUILD_DATE=UTC-$(date -u '+%Y-%m-%d') \
            --build-arg AFNI_VERSION=${AFNI_VERSION[@]} \
            --build-arg ANTS_VERSION=${ANTS_VERSION[@]} \
            --build-arg FSL_VERSION=${FSL_VERSION[@]} \
            --build-arg FREESURFER_VERSION=${FREESURFER_VERSION[@]} \
            --build-arg DCM2NIIX_VERSION=${DCM2NIIX_VERSION[@]} \
            --build-arg C3D_VERSION=${C3D_VERSION[@]} \
            -f build/tmp/Dockerfile_all .

    if [[ ${CUSTOM} == "_custom" ]]; then
        echo -e "${PROCEED}: Build \"${hint}custom${normal}\" image from radiolab_docker_${RUNTIME}."
        cp SRC/Dockerfile_custom build/tmp/Dockerfile_custom

        docker tag radiolab_docker_${RUNTIME}:latest \
                   radiolab_docker_custom:latest

        DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 \
                -t radiolab_docker_custom_${RUNTIME}:latest \
                -f build/tmp/Dockerfile_custom .

        docker image rm radiolab_docker_custom_${RUNTIME}
    fi

    echo -e "${INFORM}: Initiate Radiolabconda environment in BASH?"
    read -r -p "[Y/N] " input

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

init_radioconda=\
"# >>> Radiolabconda initialize >>>\n\
if [[ -x /radiolabdocker/startup.sh ]]; then\n\
    source /radiolabdocker/startup.sh\n\
fi\n\
# <<< Radiolabconda initialize <<<"

            if [[ ${SEL} == "N" ]]; then
                exit 1
            else
                if [[ -x ~/.bashrc ]] && \
                   [[ ! -z $(grep '# >>> Radiolabconda initialize >>>' ~/.bashrc) ]] && \
                   [[ ! -z $(grep '# <<< Radiolabconda initialize <<<' ~/.bashrc) ]]; then
                    sed "$(sed -n '/# >>> Radiolabconda initialize >>>/=' ~/.bashrc), \
                         $(sed -n '/# <<< Radiolabconda initialize <<</=' ~/.bashrc)c "${init_radioconda}"" ~/.bashrc
                else
                    echo "\n${init_radioconda}" >> ~/.bashrc
                fi
            fi

fi
