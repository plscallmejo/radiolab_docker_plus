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
echo "-c, --make-compose   Flag to make the docker-compose.yml file only, no argument is needed."
echo "                     No Docker image will be built."
echo "                     For making or upating docker-compose.yml."
echo "                     e.g. you have pulled the image from somewhere else,"
echo "                         or you already have the image built, and don't want to re-build the image."
echo "                     Note, the pre-built image should tag with "radiolab_docker:latest"."
echo "                       You can use the following command:"
echo "                         "docker tag \<pre-built image\> radiolab_docker:latest""
echo "-p, --proxy          Use proxy for image building processes."
echo "                       ????"
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./build.sh                 build the Docker image with normal runtime."
echo "./build.sh -c              make the docker-compose.yml file with normal runtime only,"
echo "                           but won't build the Docker image."
echo ""
}

# Read arguments
for arg in "$@"; do
  shift
  case "$arg" in
    "--make-compose") set -- "$@" "-c" ;;
    "--proxy")        set -- "$@" "-p" ;;
    "--help")         set -- "$@" "-h" ;;
    *)                set -- "$@" "$arg"
  esac
done

# Get runtime option
while getopts "cp:h" opt
do
    case ${opt} in
    c)
        COMPOSE="Y"
        ;;
    p)
        PROXY=${OPTARG}
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
if [[ -z ${RUNTIME} ]]; then
    RUNTIME="normal"
fi

## Generating docker-compose.yml
echo -e "${PROCEED}: Generating ${hint}docker-compose.yml${normal}"
if [[ ! -d build/tmp/ ]]; then
	mkdir -p build/tmp
fi
cp SRC/docker-compose.yml build/tmp/docker-compose.yml

## Generating ./build/tmp/Dockerfile
if [[ ${RUNTIME} = "normal" ]]; then
    if [[ -z ${COMPOSE} ]]; then
        mkdir -p build/tmp
        touch build/tmp/Dockerfile_base
        echo -e "${PROCEED}: Generating base ${hint}Dockerfile${normal}"
        echo -e "${PROCEED}: Building base image from \"${hint}ubuntu:20.04${normal}\""
        cp SRC/Dockerfile_base_normal build/tmp/Dockerfile_base
    fi
fi

# Build the docker images
if [[ -z ${COMPOSE} ]]; then
    ## Copy default Dockerfile
    cp SRC/Dockerfile_OG build/tmp/Dockerfile_OG
    cp SRC/Dockerfile_afni build/tmp/Dockerfile_afni
    cp SRC/Dockerfile_mrtrix build/tmp/Dockerfile_mrtrix
    cp SRC/Dockerfile_dsistudio build/tmp/Dockerfile_dsistudio
    cp SRC/Dockerfile_ants build/tmp/Dockerfile_ants
    cp SRC/Dockerfile_fsl build/tmp/Dockerfile_fsl
    cp SRC/Dockerfile_freesurfer build/tmp/Dockerfile_freesurfer
    cp SRC/Dockerfile_dcm2niix build/tmp/Dockerfile_dcm2niix
    cp SRC/Dockerfile_c3d build/tmp/Dockerfile_c3d
    cp SRC/Dockerfile_miniconda build/tmp/Dockerfile_miniconda
    cp SRC/Dockerfile_all build/tmp/Dockerfile_all

    ## Build base image
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_origin:latest -f build/tmp/Dockerfile_origin .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_base:latest -f build/tmp/Dockerfile_base .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_ants:latest -f build/tmp/Dockerfile_ants .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_afni:latest -f build/tmp/Dockerfile_afni .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_mrtrix:latest -f build/tmp/Dockerfile_mrtrix .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_c3d_dcm2niix_dsi:latest -f build/tmp/Dockerfile_c3d_dcm2niix_dsi .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_fsl:latest -f build/tmp/Dockerfile_fsl .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_freesurfer:latest -f build/tmp/Dockerfile_freesurfer .
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 --build-arg ALL_PROXY=${PROXY} -t radiolab_miniconda:latest -f build/tmp/Dockerfile_miniconda .
    echo -e "${PROCEED}: Base image build complete"

    # Build Docker image with proper runtime
    echo -e "${PROCEED}: Build \"${hint}radiolab${normal}\" image from base."
    DOCKER_BUILDKIT=1 docker build --ulimit nofile=122880:122880 \
            -t radiolab_docker_${RUNTIME}:latest \
            --build-arg SYS_BUILD_DATE=UTC-$(date -u '+%Y-%m-%d') \
            --build-arg ALL_PROXY=${PROXY} \
            -f build/tmp/Dockerfile_all .

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
                if [[ -f ~/.bashrc ]] && \
                   [[ ! -z $(grep '# >>> Radiolabconda initialize >>>' ~/.bashrc) ]] && \
                   [[ ! -z $(grep '# <<< Radiolabconda initialize <<<' ~/.bashrc) ]]; then
                    sed -i "$(sed -n '/# >>> Radiolabconda initialize >>>/=' ~/.bashrc),\
                            $(sed -n '/# <<< Radiolabconda initialize <<</=' ~/.bashrc)c ${init_radioconda}" ~/.bashrc
                else
                    echo -e "\n${init_radioconda}" >> ~/.bashrc
                fi
            fi

fi
