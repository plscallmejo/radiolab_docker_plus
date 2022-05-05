import os
import getpass
import shutil
import os.path as op
from radiolabdocker.miscellaneous import streamProcess

class makeCompose:
    """
    """
    def __init__(self, mount, radiolabdocker_name, radiolabdocker_img, compose_src, compose_dist, jupyter_port = "8888", fs_license = ""):
        self.user = getpass.getuser()
        self.uid = os.getuid()
        self.gid = os.getgid()
        self.home = os.path.expanduser('~')
        # check mount point
        self.mount = os.path.expanduser(mount)
        if not os.path.exists(self.mount) or not os.path.isdir(self.mount):
            raise Exception('mount path is not valid!')
        # Check if freesurfer license path is exist
        if fs_license:
            fs_license = os.path.expanduser(fs_license)
            if os.path.exists(fs_license):
                fs = ''
            else:
                fs = '#'
                fs_license = 'NotValid'
        else:
            fs = '#'
            fs_license = 'NotSupplied'
        self.jupyter_port = jupyter_port
        self.fs = fs
        self.fs_license = fs_license
        self.radiolabdocker_name = radiolabdocker_name
        self.radiolabdocker_img = radiolabdocker_img
        self.compose_src = compose_src
        self.compose_dist = os.path.expanduser(compose_dist)
        self.group = os.path.dirname(op.dirname(self.compose_dist)) + '/group'
        self.passwd = os.path.dirname(op.dirname(self.compose_dist)) + '/passwd'
    def copy(self):
        dist_dir = os.path.dirname(self.compose_dist)
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        shutil.copy(self.compose_src, self.compose_dist)
    #
    def make(self):
        # copy from source
        # read it
        self.copy()
        with open(self.compose_dist, 'r') as file:
            docker_compose = file.read()
        file.close()
        # modified the docker compose
        with open(self.compose_dist, 'w') as file:
            docker_compose = docker_compose.format(
                RADIOLAB_DOCKER = self.radiolabdocker_name,
                IMAGE = self.radiolabdocker_img,
                UID = self.uid,
                GID = self.gid,
                HOME = self.home,
                USER = self.user,
                JUPYTER_PORT = self.jupyter_port,
                MOUNT = self.mount,
                FS = self.fs,
                FS_LICENSE = self.fs_license,
                GROUP = self.group,
                PASSWD = self.passwd)
            file.write(docker_compose)
        file.close()
        # make group and passwd files
        with open(self.passwd, 'w') as file:
            file.write('{user}:x:{uid}:{gid}:{user}:{home}:/bin/bash'.format(user = self.user,
                                                                             uid = self.uid,
                                                                             gid = self.gid,
                                                                             home = self.home.replace('\\', '\\\\').replace('/', '\\/')))
        file.close()
        with open(self.group, 'w') as file:
            file.write('{user}:x:{gid}'.format(user = self.user, gid = self.gid))
        file.close()

class createContainer:
    """
    Invoke the docker-compose CMD to setup the service.
    :param compose_dist: the path to the docker-compose.yml
    """
    def __init__(self, compose_dist):
        self.compose_dist = compose_dist
    def createCommand(self):
        docker_create = 'docker-compose -f {compose_dist} up --no-start --force-recreate'.format(
                compose_dist = self.compose_dist)
        return docker_create
    def create(self):
        docker_create = self.createCommand()
        streamProcess(docker_create)

def createCMD(arguments):
    """
    """
    import pkg_resources
    from radiolabdocker.CreateContainer import makeCompose, createContainer
    from radiolabdocker.CheckStat import checkContainerStat, checkImageStat, checkVolumeStat
    from radiolabdocker.ManageContainer import startContainer
    def _create(mount,
                radiolabdocker_name,
                radiolabdocker_img,
                jupyter_port,
                fs_license,
                start,
                recreate):
        base = radiolabdocker_img.split(':')
        if len(base) == 2:
            base, tag = base
        elif len(base) == 1:
            base = base[0]
            tag = 'latest'
        exist, (status, id) = checkContainerStat(radiolabdocker_name)
        img_exist, tags = checkImageStat(base)
        compose_src = pkg_resources.resource_filename('radiolabdocker', '../config/{base}_compose/docker-compose.yml'.format(base = base))
        compose_dist = '{compose_dir}/{radiolabdocker_name}/docker-compose.yml'.format(compose_dir = compose_dir, radiolabdocker_name = radiolabdocker_name)
        if (exist and recreate) or (not exist):
            if img_exist and tag in tags:
                makeCompose(mount, radiolabdocker_name, radiolabdocker_img, compose_src, compose_dist, jupyter_port, fs_license).make()
                createContainer(compose_dist).create()
            else:
                import sys
                sys.exit('image {image} dose not exist, please build it first.'.format(image = radiolabdocker_img))
        else:
            print('container {container} setted'.format(container = radiolabdocker_name))
        if start:
            startContainer(radiolabdocker_name)
        #
    mount = arguments.mount
    jupyter_port = arguments.jupyter_port
    fs_license = arguments.fs_license
    radiolabdocker_name = arguments.container_name
    radiolabdocker_img = arguments.image
    compose_dir = arguments.compose_dir
    if arguments.start == 'False':
        start = False
    elif arguments.start == 'True':
        start = True
    if arguments.recreate == 'False':
        recreate = False
    elif arguments.recreate == 'True':
        recreate = True
    if not checkVolumeStat('radiolab_xpra_X11'):
        import docker
        docker.from_env().volumes.create('radiolab_xpra_X11')
    _create(mount, radiolabdocker_name, radiolabdocker_img, jupyter_port, fs_license, start, recreate)
    image = 'radiolab_xpra'
    base = 'radiolab_xpra'
    _create('~', base, image, '', '', start, False)
