import os.path as op
from os import makedirs
from radiolabdocker.BuildImage import buildIMAGE

tag = 'latest'
args = {"ALL_PROXY": "172.31.64.1:1080"}
base = 'xpra'

conf_path = './SRC/radiolabdocker_config.json'
log_dir = "./build/log"
dist = './build/Dockerfiles/'

if not op.exists(log_dir):
    makedirs(log_dir)

if not op.exists(dist):
    makedirs(dist)

buildIMAGE(conf_path, dist, base, tag, args, log_dir).build()