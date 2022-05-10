import os
import platform
from posixpath import islink
import shutil
import os.path as op
from turtle import home
from radiolabdocker.miscellaneous import streamProcess

class makeCompose:
    """
    """
    def __init__(self, mount, radiolabdocker_name, radiolabdocker_img, home, compose_src, compose_dist, jupyter_port = "8888", fs_license = ""):
        self.user = 'radiolabuser'
        os_type = platform.system()
        if os_type == 'Windows':
            self.uid = 1000
            self.gid = 1000
        else:
            self.uid = os.getuid()
            self.gid = os.getgid()
        # check mount point
        self.mount = os.path.abspath(os.path.expanduser(mount))
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
        self.compose_dist = os.path.abspath(os.path.expanduser(compose_dist))
        # self.home = os.path.expanduser('~')
        self.home = home
        self.hv = '' if not op.islink(home) else '#'
        self.home_volume = home if not op.islink(home) else 'NotSupplied'
        self.group = os.path.abspath(os.path.dirname(op.dirname(op.dirname(self.compose_dist))) + '/group')
        self.passwd = os.path.abspath(os.path.dirname(op.dirname(op.dirname(self.compose_dist))) + '/passwd')
    #
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
                PASSWD = self.passwd,
                HV = self.hv,
                HOME_VOLUME = self.home_volume)
            file.write(docker_compose)
        file.close()
        # make group and passwd files
        with open(self.passwd, 'w') as file:
            file.write('{user}:x:{uid}:{gid}:{user}:{home}:/bin/bash'.format(user = self.user,
                                                                             uid = self.uid,
                                                                             gid = self.gid,
                                                                             home = "/home/radiolabuser".replace('\\', '\\\\').replace('/', '\\/')))
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
                compose_dist = op.expanduser(self.compose_dist))
        return docker_create
    def create(self):
        docker_create = self.createCommand()
        streamProcess(docker_create)

def createCMD(arguments):
    """
    """
    import sys
    import pkg_resources
    from radiolabdocker.CreateContainer import makeCompose, createContainer
    from radiolabdocker.CheckStat import checkContainerStat, checkImageStat, checkVolumeStat
    from radiolabdocker.ManageContainer import startContainer
    def _create(mount,
                home_dir,
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
        compose_src = pkg_resources.resource_filename('radiolabdocker', '/config/{base}_compose/docker-compose.yml'.format(base = base))
        compose_dist = '{compose_dir}/{radiolabdocker_name}/docker-compose.yml'.format(compose_dir = compose_dir, radiolabdocker_name = radiolabdocker_name)
        if recreate or not exist:
            if img_exist and (tag in tags):
                makeCompose(mount, radiolabdocker_name, radiolabdocker_img, home_dir, compose_src, compose_dist, jupyter_port, fs_license).make()
                createContainer(compose_dist).create()
            else:
                sys.exit('error: image {image} dose not exist, please build it first.'.format(image = radiolabdocker_img))
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
    home_dir = op.abspath(op.expanduser(arguments.home_dir)) if op.islink(arguments.home_dir) else arguments.home_dir
    if (not os.path.exists(home_dir) or not os.path.isdir(home_dir)) and not op.islink(home_dir):
        if not checkVolumeStat(home_dir):
            create_home = input('create a {home_dir} volume for home dir in container (network connection may be needed)? (Y)es or (N)o\n'.format(home_dir = home_dir))
            if create_home in ['Yes', 'Y', 'yes', 'y']:
                print('creating the {home_dir}'.format(home_dir = home_dir))
                import docker
                docker.from_env().volumes.create(home_dir)
                print('setting a full privilliage to the volume ... ', end = '')
                _ = os.system('docker run -it --rm -v {home_dir}:/home/radiolabuser:z alpine:latest /bin/sh -c \'chmod 777 -R /home/radiolabuser\''.format(home_dir = home_dir))
                print('done.')
            elif create_home in ['No', 'N', 'no', 'n']:
                sys.exit('home path is not valid!')
            else:
                sys.exit('invalid input.')
    compose_dir = '~/.radiolabdocker/.config/radiolabdocker/docker-composes'
    # home_bash_src = home_dir + '/.config/radiolabdocker/bash_config'
    # bashrc_src = pkg_resources.resource_filename('radiolabdocker', '/config/bash_config/bashrc')
    # if not op.exists(home_bash_src):
    #     os.makedirs(home_bash_src)
    # if not op.exists(home_bash_src + '/bashrc'):
    #     shutil.copy(bashrc_src, home_bash_src + '/bashrc')
    # shutil.copy(home_bash_src + '/bashrc', home_dir + '/.bashrc')
    if arguments.start in ['False', 'F']:
        start = False
    elif arguments.start in ['True', 'T']:
        start = True
    else:
        sys.exit('error: \'--start\' should be either \'Ture(T)\' or \'False(F)\'')
    if arguments.recreate in ['False', 'F']:
        recreate = False
    elif arguments.recreate in ['True', 'T']:
        recreate = True
    else:
        sys.exit('error: \'--recreate\' should be either \'Ture(T)\' or \'False(F)\'')
    if not checkVolumeStat('radiolab_xpra_X11'):
        import docker
        docker.from_env().volumes.create('radiolab_xpra_X11')
    _create(mount, home_dir, radiolabdocker_name, radiolabdocker_img, jupyter_port, fs_license, start, recreate)
    image = 'radiolab_xpra'
    base = 'radiolab_xpra'
    _create('~', home_dir, base, image, '', '', start, False)
