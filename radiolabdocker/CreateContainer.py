import os
import getpass
import shutil
import subprocess
from time import sleep

class makeCompose:
    """
    """
    def __init__(self, mount, radiolabdocker_name, radiolabdocker_img, compose_src, compose_dist, port = "8888", fs_license = ""):
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
        self.port = port
        self.fs = fs
        self.fs_license = fs_license
        self.radiolabdocker_name = radiolabdocker_name
        self.radiolabdocker_img = radiolabdocker_img
        self.compose_src = compose_src
        self.compose_dist = compose_dist
    #
    def make(self):
        # copy from source
        shutil.copy(self.compose_src, self.compose_dist)
        # read it
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
                PORT = self.port,
                MOUNT = self.mount,
                FS = self.fs,
                FS_LICENSE = self.fs_license)
            file.write(docker_compose)
        file.close()

class createContainer:
    def __init__(self, compose_dist):
        self.compose_dist = compose_dist
    def createCommand(self):
        docker_create = 'docker-compose -f {compose_dist} up -d --force-recreate'.format(
                compose_dist = self.compose_dist)
        return docker_create
    def create(self):
        docker_create = self.createCommand()
        process = subprocess.Popen(docker_create, shell=True, stdout=subprocess.PIPE)
        while process.poll() is None:
            try:
                for line in iter(process.stdout.readline, b''):
                    value = line.decode("utf-8").strip()
                    if value:
                        print(value)
            except subprocess.CalledProcessError as e:
                print(f"{str(e)}")
            sleep(0.1)

mount = '~/Downloads'
port = 8888
fs_license = './build/tmp/license.txt'
radiolabdocker_name = 'radiolab_docker'
radiolabdocker_img = 'radiolab_docker'
compose_src = './SRC/docker-compose.yml'
compose_dist = './build/tmp/radiolab_docker/docker-compose.yml'
a = makeCompose(mount, radiolabdocker_name, radiolabdocker_img, compose_src, compose_dist, port, fs_license)
a.make()
b = createContainer(compose_dist)
b.create()