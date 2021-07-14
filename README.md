# radiolab_docker

Tools for constructing, managing, and depositing a robust and reproducible neuroimage analysis environment. 

## Usage
`build.sh`

Build the basic Dockerfile and docker-docker-compose.yml,
then build the Docker image from the begining.


```
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

Create a radiolab_docker.


```
Usage: ./create.sh [data_path] [freesurfer_license]

Specify the "data_path" to be mounted to /DATA in inside the container.
Note, the "data_path" should be a DIR,
      and you are supposed to own the rwx permissions to it.

EXAMPLES:
./create.sh /the/path/to/your/data
```


`run.sh`

Run the "radiolab_docker".


```
Usage: ./run.sh [options]

-p, --fsl-parallel   Flag to specify the num of threads for fsl_sub.
                       0 -- off
                       1 -- on, maximum num of cores available
                       Or any num < maximum of cores
                       Note, left it unflag to a default setting
                          number of threads for fsl_sub will set to 
                          maximum num of cores - 2 (n - 2)
-h, --help           Show this message.

Examples:
./run.sh             Enter the interactive shell with \$FSLPARALLEL=\$(echo "\$\(nproc\)-2" | bc),
                       which means number of threads for fsl_sub will set to maximum num of cores - 2 (n - 2)
./run.sh -p 6        Enter the interactive shell with \$FSLPARALLEL=6,
                       which means fsl_sub will run in 6 threads
```


`save.sh`

Save "radiolab_docker" image to a tar.gz archive file.

Actually, the script can be used for more general
purpose to store any docker image as \*.tar.gz.


```
Usage: ./save.sh -o [path] -i [image name]
-o, --output-path    Specify the output path.
                       If no file name is given,
                       "radiolab_docker-$(date -u '+%Y%m%d').tar.gz" will be
                       set as default.
-i, --image          Specify the image to be store.
                       If not specify, radiolab:latest will be selected.
-b, --bar            Show progress bar (needs pv and jq command).
                       T for TRUE, and F for FALSE. (default: T)
-h, --help           Show this message.

Examples:
./save.sh -o /some/path/
                     Save radiolab:latest to "/some/path/radiolab_docker-$(date -u '+%Y%m%d').tar.gz"
./save.sh -o /some/path/foo.tar.gz
                     Save radiolab:latest to "/some/path/foo.tar.gz"
Or, more general usege,
./save.sh -o /some/path/foo.tar.gz -i bar:tag
                     Save bar:tag to "/some/path/foo.tar.gz"
```


`load.sh`

Load docker image.

Note that the image should store as "tar.gz",
and generate using "docker save [image]:[tag] | gzip > [image].tar.gz",
thus gunzip can decompress the tarball as stdout which further pipe to
the "docker load" command.


```
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
Permission issue in first time docker installation: `$USER` should be in the `docker` group, run the following
command,

`sudo usermod -aG docker $USER`

and then, reboot.


AFNI font garbled: this might due to missing x server font in the host system,
installing `xorg-xfont-100dpi` and `xorg-xfont-75dpi` might fix the issue.

Issue about openGL library: some applications will use the openGL library, such as `freeview` and `suma` etc., 
if errors pop-up, try to set a different `LIBGL_ALWAYS_INDIRECT` value (either 0 or 1).


## Acknowledge
The Dockerfile_OG was originally based on a Dockerfile generated by [neurodocker](https://github.com/ReproNim/neurodocker),
that is a great work! 

