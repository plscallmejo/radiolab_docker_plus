import os
import getpass
import shutil
from radiolabdocker.miscellaneous import streamProcess

class makeCompose:
    """
    """
    def __init__(self, mount, radiolabdocker_name, radiolabdocker_img, compose_src, compose_dist, jupyter_port = "8888", fs_license = ""):
        self.user = getpass.getuser()
        self.uid = os.getuid()
        self.gid = os.getgid()
        self.home = os.path.expanduser('~')
        # TODO: check mount point
        self.mount = mount
        # Check if freesurfer license path is exist
        if fs_license:
            fs_license = os.path.abspath(fs_license)
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
        self.compose_dist = compose_dist
    def copy(self):
        dist_dir = os.path.dirname(self.compose_dist)
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        shutil.copy(self.compose_src, self.compose_dist)
        return 0
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
                FS_LICENSE = self.fs_license)
            file.write(docker_compose)
        file.close()

class createContainer:
    """
    Invoke the docker-compose CMD to setup the service.
    :param compose_dist: the path to the docker-compose.yml
    """
    def __init__(self, compose_dist):
        self.compose_dist = compose_dist
    def createCommand(self):
        docker_create = 'docker-compose -f {compose_dist} up -d --force-recreate'.format(
                compose_dist = self.compose_dist)
        return docker_create
    def create(self):
        docker_create = self.createCommand()
        streamProcess(docker_create)

