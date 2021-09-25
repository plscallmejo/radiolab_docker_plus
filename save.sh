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
echo "Save "radiolab_docker" image to a tar.gz archive file."
echo "Actually, the script can be used for more general"
echo "purpose to store any docker image as *.tar.gz."
echo ""
echo "Usage: ./save.sh -o [path] -i [image name]"
echo "-o, --output-path    Specify the output path."
echo "                       If no file name is given,"
echo '                       "radiolab_docker_normal-$(date -u '+%Y%m%d').tar.gz" will be'
echo "                       set as default."
echo "-i, --image          Specify the image to be store."
echo "                       If not specify, radiolab_docker_normal:latest will be selected."
echo "-b, --bar            Show progress bar (needs pv and jq command)."
echo "                       T for TRUE, and F for FALSE. (default: T)"
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./save.sh -o /some/path/"
echo '                     Save radiolab_docker_normal:latest to "/some/path/radiolab_docker_normal-$(date -u '+%Y%m%d').tar.gz"'
echo "./save.sh -o /some/path/foo.tar.gz"
echo "                     Save radiolab_docker_normal:latest to "/some/path/foo.tar.gz""
echo "Or, more general usege,"
echo "./save.sh -o /some/path/foo.tar.gz -i bar:tag"
echo "                     Save bar:tag to "/some/path/foo.tar.gz""
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

if [[ -z ${save_path_og} ]]; then
    echo -e "${ERROR}: Specify the path with an "-o" flag."
    Usage
    exit 1
fi

if [[ -z ${image} ]]; then
    image="radiolab_docker_normal:latest"
    echo -e "${WARNING}: No image name supplied, \"${hint}${image}${normal}\" is automatically selected."
fi

image_base_tag=( `echo ${image} | sed -e 's/:/ /g'` )
image_base=${image_base_tag[0]}

echo -e "${PROCEED}: Check if the \"${hint}${image}${normal}\" is valid ... \c"
check_img="$(docker inspect ${image} 2>&1 > /dev/null)"
if [[ -z ${check_img} ]]; then
    echo -e "${proceed}Passed${normal}."
else
    echo -e "${error}Failed${normal}."
    echo -e "${ERROR}: Error when checking the image \"${hint}${image}${normal}\", maybe the image \"${hint}${image}${normal}\" dosen't exist, please check again!"
    Usage
    exit 1
fi

if [[ -z ${BAR} ]] || [[ ${BAR} == "T" ]]; then
    check_pv="$(command -V pv 2> /dev/null)"
    check_jq="$(command -V jq 2> /dev/null)"
    if [[ ${check_pv} ]] && [[ ${check_jq} ]]; then
        size=`docker inspect ${image} | jq '.[].Size'`
        bar="pv -tpeIrb -s ${size} |"
    else
        echo -e "${WARNING}: Either "pv" and "jq" command is not found, the progress bar will not display."
        bar=""
    fi
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
            save_path_filename=${image_base}-$(date -u '+%Y%m%d').tar.gz
            echo -e "${WARNING}: No filename supplied, docker image will automatically save as \"${hint}${save_path_dir}/${save_path_filename}${normal}\"."
        else
            if [[ "${save_path_filename: -7}" != ".tar.gz" ]]; then
                echo -e "${ERROR}: The output file should be a \"${hint}*.tar.gz${normal}\" file! Please check again!"
                Usage
                exit 1
            fi
        fi
    fi
fi

echo -e "${PROCEED}: Saving ${image} to \"${hint}${save_path_dir}/${save_path_filename}${normal}\"."
bash -c "docker save ${image} | ${bar} gzip > ${save_path_dir}/${save_path_filename}"

