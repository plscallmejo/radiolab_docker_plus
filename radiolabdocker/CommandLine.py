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
    parser = argparse.ArgumentParser(description = '???')
    subparser = parser.add_subparsers()

    # 'build' CMD
    cmd_build = subparser.add_parser('build', help = '???')
    cmd_build.add_argument('base', action='store', nargs='?', default='radiolab_docker:latest', help='???')
    cmd_build.add_argument('--dockerfile_dir', '-d', action='store', nargs='?', default='~/.radiolabdocker/Dockerfiles', help='???')
    cmd_build.add_argument('--proxy', '-p', action='store', default=argparse.SUPPRESS, help='???')
    cmd_build.add_argument('--rebuild', '-r', action='store', default='False', help='???')
    cmd_build.add_argument('--force_rebuild', '-f', action='store', default='False', help='???')
    cmd_build.set_defaults(func = build)

    # 'create' CMD
    cmd_run = subparser.add_parser('create', help = '???')
    cmd_run.add_argument('--image', '-i', action='store', nargs='?', default='radiolab_docker', help='???')
    cmd_run.add_argument('--container_name', '-n', action='store', nargs='?', default='radiolab_docker', help='???')
    cmd_run.add_argument('--compose_dir', '-d', action='store', nargs='?', default='~/.radiolabdocker/docker-composes', help='???')
    cmd_run.add_argument('--mount', '-m', action='store', nargs='?', default='./', help='???')
    cmd_run.add_argument('--fs_license', '-l', action='store', nargs='?', default='', help='???')
    cmd_run.add_argument('--jupyter_port', action='store', nargs='?', default='8888', help='???')
    cmd_run.add_argument('--start', '-s', action='store', nargs='?', default='False', help='???')
    cmd_run.add_argument('--recreate', '-r', action='store', nargs='?', default='False', help='???')
    cmd_run.set_defaults(func = create)

    # 'save' CMD
    cmd_run = subparser.add_parser('save', help = '???')
    cmd_run.add_argument('path', action='store', nargs='?', default='./', help='???')
    cmd_run.add_argument('image', action='store', nargs='*', default='radiolab_docker:latest', help='???')
    cmd_run.set_defaults(func = save)

    # 'load' CMD
    cmd_run = subparser.add_parser('load', help = '???')
    cmd_run.add_argument('tarball', action='store', nargs='*', default='', help='???')
    cmd_run.set_defaults(func = load)

    # 'start' CMD
    cmd_run = subparser.add_parser('start', help = '???')
    cmd_run.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='???')
    cmd_run.set_defaults(func = Cstart)

    # 'stop' CMD
    cmd_run = subparser.add_parser('stop', help = '???')
    cmd_run.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='???')
    cmd_run.set_defaults(func = Cstop)

    # 'pause' CMD
    cmd_run = subparser.add_parser('pause', help = '???')
    cmd_run.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='???')
    cmd_run.set_defaults(func = Cpause)

    # 'unpause' CMD
    cmd_run = subparser.add_parser('unpause', help = '???')
    cmd_run.add_argument('container_name', action='store', nargs='*', default='radiolab_docker', help='???')
    cmd_run.set_defaults(func = Cunpause)

    # 'run' CMD
    cmd_run = subparser.add_parser('run', help = '???')
    cmd_run.add_argument('container_name', action='store', nargs='?', default='radiolab_docker', help='???')
    cmd_run.set_defaults(func = run)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        args = parser.parse_args(['-h'])
    args.func(args)