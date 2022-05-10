import argparse

def build(arguments):
    from radiolabdocker.BuildImage import buildCMD
    buildCMD(arguments)

def create(arguments):
    from radiolabdocker.CreateContainer import createCMD
    createCMD(arguments)

def Cstart(arguments):
    from radiolabdocker.ManageContainer import startContainer
    for container_name in arguments.container_name:
        startContainer(container_name)

def Cstop(arguments):
    from radiolabdocker.ManageContainer import stopContainer
    for container_name in arguments.container_name:
        stopContainer(container_name)

def Cpause(arguments):
    from radiolabdocker.ManageContainer import pauseContainer
    for container_name in arguments.container_name:
        pauseContainer(container_name)

def Cunpause(arguments):
    from radiolabdocker.ManageContainer import unpauseContainer
    for container_name in arguments.container_name:
        unpauseContainer(container_name)

def Cremove(arguments):
    from radiolabdocker.ManageContainer import removeContainer
    for container_name in arguments.container_name:
        removeContainer(container_name, arguments.force_remove)

def run(arguments):
    from radiolabdocker.RunContainer import runpty
    runpty(arguments.container_name)

def save(arguments):
    from radiolabdocker.SaveLoadImage import saveCMD
    for image in arguments.image:
        saveCMD(arguments.path, image)

def load(arguments):
    from radiolabdocker.SaveLoadImage import loadCMD
    for tarball in arguments.tarball:
        loadCMD(tarball)

def cli():
    # Setup the arg parser
    parser = argparse.ArgumentParser(description = 'A fully upgraded version of radiolab_docker.')
    subparser = parser.add_subparsers(title="actions")

    # 'build' CMD
    cmd_build = subparser.add_parser('build', help = 'Build the radiolab_docker plus images.')
    cmd_build.add_argument('-b', '--base', action='store', nargs='?', default='radiolab_docker:latest', help='the base name of the target, default: radiolab_docker:latest.')
    cmd_build.add_argument('-d', '--dockerfile_dir', action='store', nargs='?', default='~/.radiolabdocker/.config/radiolabdocker/Dockerfiles', help='the folder to save the dockerfiles, default: ~/.radiolabdocker/.config/radiolabdocker/Dockerfiles.')
    cmd_build.add_argument('-p', '--proxy', action='store', nargs='?', default=argparse.SUPPRESS, help='set the proxy while building the images, the argument will be passed to ALL_PROXY in the intermediate containers.')
    cmd_build.add_argument('-r', '--rebuild', action='store', nargs='?', default='False', help='rebuild the targatting imagey.')
    cmd_build.add_argument('-f', '--force_rebuild', action='store', nargs='?', default='False', help='rebuild all the images, (T)rue or (F)alse, default: False.')
    cmd_build.set_defaults(func = build)

    # 'create' CMD
    cmd_create = subparser.add_parser('create', help = 'create the raiolab_docker plus containers.')
    cmd_create.add_argument('-i', '--image', action='store', nargs='?', default='radiolab_docker:latest', help='specified the image to create container, default: radiolab_docker.')
    cmd_create.add_argument('-n', '--container_name', action='store', nargs='?', default='radiolab_docker', help='specified the container name (use it for instance of working with different projects), default: radiolab_docker.')
    cmd_create.add_argument('-m', '--mount', action='store', nargs='?', default='~/.radiolabdocker', help='specified the mounting point, default: ~/.radiolabdocker.')
    cmd_create.add_argument('-s', '--start', action='store', nargs='?', default='False', help='start the container after creating, (T)rue or (F)alse, default: False.')
    cmd_create.add_argument('-l', '--fs_license', action='store', nargs='?', default='', help='provide the freesurfer license')
    cmd_create.add_argument('-r', '--recreate', action='store', nargs='?', default='False', help='force re-create the container, (T)rue or (F)alse, default: False.')
    cmd_create.add_argument('-p', '--jupyter_port', action='store', nargs='?', default='8888', help='the host port for jupyter hub, default:8888.')
    cmd_create.add_argument('--home_dir', action='store', nargs='?', default='~/.radiolabdocker', help='the home of the creating container, default: ~/.radiolabdocker.')
    cmd_create.set_defaults(func = create)

    # 'save' CMD
    cmd_save = subparser.add_parser('save', help = 'save the images.')
    cmd_save.add_argument('image', action='store', nargs='*', default='radiolab_docker:latest', help='specified the image(s) to be saved, default: radiolab_docker:latest.')
    cmd_save.add_argument('path', action='store', nargs='?', default='./', help='the folder path for the resulting archive(s).')
    cmd_save.set_defaults(func = save)

    # 'load' CMD
    cmd_load = subparser.add_parser('load', help = 'load the tag.gz archive that saved with `radiolabdocker save` or `docker save` and pipe stdout to gzip.')
    cmd_load.add_argument('tarball', action='store', nargs='*', default='', help='the path to the tar.gz archive file.')
    cmd_load.set_defaults(func = load)

    # 'start' CMD
    cmd_start = subparser.add_parser('start', help = 'start the container(s).')
    cmd_start.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='the name(s) of the container(s), default: radiolab_docker.')
    cmd_start.set_defaults(func = Cstart)

    # 'stop' CMD
    cmd_stop = subparser.add_parser('stop', help = 'stop the container(s)')
    cmd_stop.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='the name(s) of the container(s), default: radiolab_docker.')
    cmd_stop.set_defaults(func = Cstop)

    # 'pause' CMD
    cmd_pause = subparser.add_parser('pause', help = 'pause the container(s).')
    cmd_pause.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='the name(s) of the container(s), default: radiolab_docker.')
    cmd_pause.set_defaults(func = Cpause)

    # 'unpause' CMD
    cmd_unpause = subparser.add_parser('unpause', help = 'unpause the container(s).')
    cmd_unpause.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='the name(s) of the container(s), default: radiolab_docker.')
    cmd_unpause.set_defaults(func = Cunpause)

    # 'remove' CMD
    cmd_remove = subparser.add_parser('remove', help = 'remove a container(s).')
    cmd_remove.add_argument('-f', '--force_remove', action='store', nargs='?', default='False', help='force to remove, (T)rue or (F)alse, default: False.')
    cmd_remove.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='the name(s) of the container(s), default: radiolab_docker.')
    cmd_remove.set_defaults(func = Cremove)

    # 'run' CMD
    cmd_run = subparser.add_parser('run', help = 'enter the shell to a running container')
    cmd_run.add_argument('container_name', action='store', nargs='?', default='radiolab_docker', help='the name of the targeting container, default: radiolab_docker.')
    cmd_run.set_defaults(func = run)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        args = parser.parse_args(['-h'])
    args.func(args)

if __name__ == '__main__':
    cli()