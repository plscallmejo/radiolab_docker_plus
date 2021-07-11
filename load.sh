#!/bin/bash

# Set colors
normal="\033[0m"
error="\033[41;33m"
proceed="\033[42;30m"
inform="\033[46;30m"
hint="\033[4;36m"
ERROR="${error}ERROR${normal}"
PROCEED="${proceed}PROCEEDING${normal}"
INFORM="${inform}INFORM${normal}"

Usage () {
echo ""
echo "Load docker image."
echo "Note that the image should store as "tar.gz","
echo 'and generate using "docker save [image]:[tag] | gzip > [image].tar.gz",'
echo "thus gunzip can decompress the tarball as stdout which further pipe to"
echo "the "docker load" command."
echo ""
echo "Usage: ./load.sh [path/to/image.tar.gz] [OPTIONS]"
echo "-b, --bar            Show progress bar (needs pv command)."
echo "                       T for TRUE, and F for FALSE. (default: T)"
echo "-h, --help           Show this message."
echo ""
echo "Examples:"
echo "./load.sh /path/to/tar.gz"
echo "                     Load the docker image from /path/to/tar.gz."
echo "./load.sh -b F /path/to/tar.gz"
echo "                     Load the docker image from /path/to/tar.gz and"
echo "                       disable the progress bar."
echo ""
}

for arg in "$@"; do
  shift
  case "$arg" in
    "--help") set -- "$@" "-h" ;;
    "--bar")  set -- "$@" "-b" ;;
    *)        set -- "$@" "$arg"
  esac
done

# Get fsl parallelism
while getopts "b:h" opt
do
    case ${opt} in
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

check_pv="$(command -V pv 2> /dev/null)"
if [[ ${check_pv} ]]; then
    bar="pv | "
else
    echo -e "${WARNING}: "pv" command is not found, the progress bar will not display."
    bar=""
fi

shift $((OPTIND - 1))
tar_path="$@"
check_dir=`readlink -e ${tar_path}`
tar_path_dir=`dirname ${tar_path}`
tar_path_filename=`basename ${tar_path}`

if [[ -d ${check_dir} ]]; then
    echo -e "${ERROR}: The path is a directory, a "tar.gz" file is expected."
    Usage
    exit 1
fi

if [[ ! -f ${tar_path} ]]; then
    echo -e "${ERROR}: File not exist."
    Usage
    exit 1
elif [[ "${tar_path_filename: -7}" != ".tar.gz" ]]; then
    echo -e "${ERROR}: The input file should be a \"${hint}*.tar.gz${normal}\" file! Please check again!"
    Usage
    exit 1
fi

echo -e "${PROCEED}: Loading (Restoring) docker image from \"${hint}${tar_path}${normal}\""
bash -c "gunzip -c ${tar_path} | ${bar} docker load"
