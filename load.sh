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
echo "Run the "${hint}radiolab_docker${normal}""
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
    "--fsl-parallel") set -- "$@" "-p" ;;
    "--help") set -- "$@" "-h" ;;
    *)        set -- "$@" "$arg"
  esac
done

# Get fsl parallelism
while getopts "p:h" opt
do
    case ${opt} in
    p)
        FSL_PARA=${OPTARG}
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

gunzip -c ubuntu.tar.gz | pv -tperb -s $(gzip -l ubuntu.tar.gz | awk 'FNR == 2 {print $2}') | docker load
