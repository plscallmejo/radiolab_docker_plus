#!/bin/bash

# Set colors
normal="\033[0m"
error="\033[41;33m"
proceed="\033[42;30m"
warning="\033[43;31m"
inform="\033[46;30m"
hint="\033[4;36m"
INFORM="${inform}INFORM${normal}"
ERROR="${error}ERROR${normal}"
WARNING="${warning}WARNING${normal}"
PROCEED="${proceed}PROCEEDING${normal}"

Usage () {
echo ""
echo "Save "radiolab_docker" image."
echo "-p, --path           "
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./save.sh            Save"
echo "                       which means number of threads for fsl_sub will set to maximum num of cores - 2 (n - 2)"
echo "./run.sh -p 6        Enter the interactive shell with \$FSLPARALLEL=6,"
echo "                       which means fsl_sub will run in 6 threads"
echo ""
}

for arg in "$@"; do
  shift
  case "$arg" in
    "--output-path") set -- "$@" "-o" ;;
    "--image")       set -- "$@" "-i" ;;
    "--bar")         set -- "$@" "-b" ;;
    "--help")        set -- "$@" "-h" ;;
    *)               set -- "$@" "$arg"
  esac
done

# Get fsl parallelism
while getopts "o:i:b:h" opt
do
    case ${opt} in
    o)
        save_path_og=${OPTARG}
        ;;
    i)
        image=${OPTARG}
        ;;
    b)
        BAR=${OPTARG}
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

if [[ -z ${image} ]]; then
    image="radiolab:latest"
    echo -e "${WARNING}: no image name supplied, \"${hint}${image}${normal}\" is automatically selected."
fi

echo -e "${PROCEED}: check if the ${image} is valid."
check_img="$(docker inspect ${image} 2>&1 > /dev/null)"
if [[ -z ${check_img} ]]; then
    echo -e "${INFORM}: image check pass."
else
    echo -e "${ERROR}: error when checking the image ${image}, maybe the ${image} dosen't exist, please check again!"
    Usage
    exit 1
fi

if [[ -z ${BAR} ]] || [[ ${BAR} == "T" ]]; then
    size=`docker inspect ${image} | jq '.[].Size'`
    bar="pv -tpeIrb -s ${size} |"
elif [[ ${BAR} == "F" ]]; then
    bar=""
else
    echo -e "${ERROR}: Invalid -b, --bar option."
    Usage
    exit 1
fi

if [[ -z ${save_path_og} ]]; then
    echo -e "${ERROR}: Please specify the save path!"
    Usage
    exit 1
else
    check_dir=`readlink -e ${save_path_og}`
    save_path_dir=`dirname ${save_path_og}`
    save_path_filename=`basename ${save_path_og}`
    if [[ -d ${check_dir} ]]; then
        save_path_dir=${save_path_dir}/${save_path_filename}
        save_path_filename=""
    fi

    if [[ -z ${save_path_dir} ]]; then
        echo -e "${ERROR}: The output path \"${hint}${save_path}${normal}\" is invalid! Please check again!"
        Usage
        exit 1
    else
        if [[ -z ${save_path_filename} ]]; then
            save_path_filename=radiolab_docker-$(date -u '+%Y%m%d').tar.gz
            echo -e "${WARNING}: no filename supplied, docker image will automatically save as \"${hint}${save_path_dir}/${save_path_filename}${normal}\"."
        else
            if [[ "${save_path_filename: -7}" != ".tar.gz" ]]; then
                echo -e "${ERROR}: the output file should be \"${hint}*.tar.gz${normal}\"! Please check again!"
                Usage
                exit 1
            fi
        fi
    fi
fi


echo -e "${PROCEED}: saving ${image} to ${save_path_dir}/${save_path_filename}"
bash -c "docker save ${image} | ${bar} gzip > ${save_path_dir}/${save_path_filename}"
