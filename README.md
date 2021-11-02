# radiolab_docker

Tools for constructing, managing, and deploying a robust and reproducible neuroimage analysis environment.

## Included softwares
* AFNI
* ANTs
* FSL
* Freesuefer
* convert3D
* dcm2niix
* miniconda (Radiolabconda environment with py3.7 numpy pandas scipy matplotlib seaborn sk-learn tensorflow pytorch pydicom nipype graphviz pydot nibabel pybids dipy qsiprep nilearn)

# Requirement
## Linux (Ubuntu, Manjaro, etc),
* docker (19.03, or newer)
* docker-compose
* `xhost` command (probably a default in many distributions)
* `pv` and `jq` command (optional, for progress bar display)

## Window 10 (1903 build 18362 or newer (on x64), wsl2 enabled, docker desktop with WSL2 backend)
* docker desktop for window (2.2.0.4, or newer)
* git for windows, or MSYS2 (git bash should be enough; for MSYS2, `git` and `winpty` should be installed)
* VcXsrv (Uncheck the `native opengl` and check the `Disable access control`)

## Windows 11 with built-in GPU and linux gui support in wsl2.
* But still needs VcXsrv for the reason that AFNI gui is suck with the win11 built-in linux gui. Just run AFNI as follow,
`DISPLAY=host.docker.internal:0 afni`

# Installation
Git clone the current repo, cd to radiolab_docker, run the scripts, and have fun!
```
git clone https://github.com/plscallmejo/radiolab_docker
```

## Usage
`build.sh`

```
Build the basic Dockerfiles and docker-compose.yml,
then build the Docker images from the begining (buildx implement).

Usage: ./build.sh [options]
-r, --runtime        Specify the RUNTIME, either "normal" or "nvidia". (default: normal)
-c, --make-compose   Flag to make the docker-compose.yml file only, no argument is needed.
                     No Docker image will be built.
                     For making or upating docker-compose.yml.
                     e.g. you have pulled the image from somewhere else,
                         or you already have the image built, and don't want to re-build the image.
                     Note, the pre-built image should tag with "radiolab_docker:latest".
                       You can use the following command:
                         "docker tag \<pre-built image\> radiolab_docker:latest"
-s, --cn-sp          Use some cn speacialized setting.
                       T for TRUE, and F for FALSE. (default: T)
-h, --help           Show this message.

Examples:
./build.sh -r nvidia       build the Docker image using nvidia runtime.
./build.sh -r nvidia -c    make the docker-compose.yml file with nvidia runtime only,
                           but won't build the Docker image.
./build.sh -r normal       build the Docker image with normal runtime.
or ./build.sh
./build.sh -c              make the docker-compose.yml file with normal runtime only,
                           but won't build the Docker image.
```


`create.sh`

```
Create a radiolab_docker container.

Usage: ./create.sh -p [data_path] -l [freesurfer_license] -r [runtime]
-r, --runtime        Specify the RUNTIME, either "normal" or "nvidia". (default: normal)
-p, --data-path      Specify the "data_path" to be mounted to /DATA in inside the container.
                         Note, the "data_path" should be a DIR,
                         and you are supposed to own the rwx permissions to it.
-c, --custom         Run customized "radiolab_docker" image.
-n, --name           Specify the service name of the container. (default: radiolab_docker)
-b, --jupyter-binding-port   Specify the local port for jupyter-notebook. (default: 8888)
-l, --fs-license     Specify the Freesurfer license for a full functional Freesurfer.
```


`run.sh`

```
Run "radiolab_docker" container.
then build the Docker image from the begining.

Usage: ./run.sh [options]
-n, --container-name   Specify the container name. (default: radiolab_dock)
-h, --help           Show this message.
```


`save.sh`

```
Save "radiolab_docker" image to a tar.gz archive file.
Actually, the script can be used for more general
purpose to store any docker image as *.tar.gz.

Usage: ./save.sh -o [path] -i [image name]
-o, --output-path    Specify the output path.
                       If no file name is given,
                       "radiolab_docker_normal-$(date -u '+%Y%m%d').tar.gz" will be'
                       set as default.
-i, --image          Specify the image to be store.
                       If not specify, radiolab_docker_normal:latest will be selected.
-b, --bar            Show progress bar (needs pv and jq command).
                       T for TRUE, and F for FALSE. (default: T)
-h, --help           Show this message.

Examples:
./save.sh -o /some/path/
                     Save radiolab_docker_normal:latest to "/some/path/radiolab_docker_normal-$(date -u '+%Y%m%d').tar.gz"'
./save.sh -o /some/path/foo.tar.gz
                     Save radiolab_docker_normal:latest to "/some/path/foo.tar.gz"
Or, more general usege,
./save.sh -o /some/path/foo.tar.gz -i bar:tag
                     Save bar:tag to "/some/path/foo.tar.gz"
```


`load.sh`

```
Load docker image.
Note that the image should store as "tar.gz",
and generate using "docker save [image]:[tag] | gzip > [image].tar.gz",'
thus gunzip can decompress the tarball as stdout which further pipe to
the "docker load" command.

Usage: ./load.sh [path/to/image.tar.gz] [OPTIONS]
-b, --bar            Show progress bar (needs pv command).
                       T for TRUE, and F for FALSE. (default: T)
-h, --help           Show this message.

Examples:
./load.sh /path/to/tar.gz
                     Load the docker image from /path/to/tar.gz.
./load.sh -b F /path/to/tar.gz
                     Load the docker image from /path/to/tar.gz and
                       disable the progress bar.
```


## Known Issues

### docker execution permissions
Permission issue in first time docker installation: `$USER` should be in the `docker` group, run the following
command,

`sudo usermod -aG docker $USER`

then, reboot.


### AFNI garble fonts
AFNI font garbled: this may due to missing x server font in the host system,
installing `xorg-xfont*` packages may fix the issue.

### OpenGL issues
Issue about openGL library: some applications will use the openGL library, such as `freeview` and `suma` etc.,
if errors, try to set a different `LIBGL_ALWAYS_INDIRECT` value (either 0 or 1).

### Jupyter web application
In order to login Jupyter notebook/lab in the host web browser, jupyter should execution with a `--ip 0.0.0.0` flag, as follows,
```
jupyter lab/notebook --ip 0.0.0.0
```
Also note, run jupyter in the firefox inside the container with VcXsrv maybe slow, to avoid popping up of the firefox, use following,
```
jupyter lab/notebook --ip 0.0.0.0 --no-browser
```

## Acknowledgements
The Dockerfile_OG was originally based on a Dockerfile generated by [neurodocker](https://github.com/ReproNim/neurodocker),
that is a great work!
    
