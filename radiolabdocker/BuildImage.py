import os
import docker
import re
from MakeDockerfile import DockerConfig

class buildIMAGE:
#
#
    def __init__(self, conf_path, dist, base, tag, args, log_dir = ''):
        self.config = DockerConfig(conf_path, dist, base)
        self.tag = 'radiolab_{base}:{tag}'.format(
            base = base,
            tag = tag
        )
        self.args = args
        self.path = dist
        self.dist = self.config.dist
        if log_dir == '':
            self.loggin = 0
            self.log_path = log_dir
        else:
            self.loggin = 1
            self.log_path = '{log_dir}/radiolabdocker_{base}.log'.format(
                log_dir = log_dir,
                base = base
            )
    #
    def mkDockerfile(self):
        self.config.mkDockerfile()
    #
    def build(self):
        pattern = r'\x1B\[(([0-9]{1,2})?(;)?([0-9]{1,2})?)?[m,K,H,f,J]'
        os.environ["DOCKER_BUILDKIT"] = "1"
        self.mkDockerfile()
        client = docker.from_env()
        self.log = client.from_env().api.build(
            path = '.',
            dockerfile = self.dist,
            tag = self.tag,
            buildargs = self.args,
            decode = True,
            quiet = False)
        if self.loggin == 1:
            try:
                log_file = open(self.log_path, 'w')
                log_file.close()
            except:
                self.loggin = 0
        for line in self.log:
            if list(line.keys())[0] in ('stream', 'error'):
                value = list(line.values())[0].strip()
                if value:
                    print(value)
                    if self.loggin == 1:
                        log_file = open(self.log_path, 'a')
                        log_file.write(re.sub(pattern, '', value) + "\n")
                        log_file.close()

conf_path = '../SRC/radiolabdocker_config.json'
log_dir = "../build/log"
dist = '../build/Dockerfiles/'
base = 'origin'
tag = 'latest'
args = {"ALL_PROXY": "172.31.64.1:1080"}
buildIMAGE(conf_path, dist, base, tag, args, log_dir).build()
base = 'xpra'
buildIMAGE(conf_path, dist, base, tag, args, log_dir).build()