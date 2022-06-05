from email.mime import base
import os
import os.path as op
import json
import datetime
from os import makedirs
from radiolabdocker.miscellaneous import streamProcess

class DockerConfig:
    """
    Make a Dockerfile according to the config file.
    :param conf_path: path to config file.
    :param dist: path to the Dockerfile dir, the Dockerfile will be renamed to Dockerfile_{base}.
    :param base: the configured base name of the image.
    """
    def __init__(self, conf_path, dist, base):
        # read the config file
        with open(conf_path, 'r') as f:
            config = json.load(f)[base]
        f.close()
        # Basic info
        self.base = base
        self.config = config
        # Validate the config
        ## TODO
        # Config steps sequently
        self.steps = dict()
        try:
            self.steps['FROM '] = config['img']
        except:
            pass
        try:
            self.steps['USER '] = config['user']
        except:
            pass
        try:
            self.steps['ARG '] = config['args']
        except:
            pass
        try:
            self.steps['ENV '] = config['envs']
        except:
            pass
        try:
            self.steps['RUN --mount=type=bind,'] = config['bind_copy']
        except:
            pass
        try:
            self.steps['COPY '] = config['copy']
        except:
            pass
        try:
            self.steps['RUN '] = config['commands']
        except:
            pass
        try:
            self.steps['ENTRYPOINT '] = config['entry']
        except:
            pass
        # apt install packages
        try:
            self.apts = config['apt']
        except:
            pass
        # tarball packages config
        try:
            self.tar = config['tar']
        except:
            pass
        # zipfile packages config
        try:
            self.zip = config['zip']
        except:
            pass
        # conda install packages (installed in radiodocker environment)
        try:
            self.conda = config['conda']
        except:
            pass
        # pip install packages (installed in radiodocker environment)
        try:
            self.pip = config['pip']
        except:
            pass
        # Bind copy to grab softwares in other image
        try:
            self.bind = config['bind_file']
        except:
            pass
        # Copy file externally
        try:
            self.copy = config['copy_file']
        except:
            pass
        # Make packages from git (use cmake command, maybe just for ANTS. ^-^)
        try:
            self.git_make = config['git_make']
        except:
            pass
        # Build packages from git (./configure ./build)
        try:
            self.git_build = config['git_build']
        except:
            pass
        self.dist = op.join(dist, "Dockerfile_" + base)
    # Write the Dockerfile
    def mkDockerfile(self):
        # Check the current line, and set the (indent, start, end) for a line
        def identifyLine(l, length, head):
                # The first line
                if l == 1:
                    # One line command
                    if l == length:
                        return ('', head, '\n')
                    # The first line of multiple lines
                    else:
                        return ('', head, ' \\\n')
                #
                if l != 1:
                    # The final line
                    if l == length:
                        return (' ' * 4, '', '\n')
                    # Not the end
                    else:
                        return (' ' * 4, '', ' \\\n')
        def identifyEntryLine(l, length, head):
                # The first line
                if l == 1:
                    # One line command
                    if l == length:
                        return ('', head + '["', '\"]\n')
                    # The first line of multiple lines
                    else:
                        return ('', head + '[ \\\n' + ' ' * 4 + '\"', '\", \\\n')
                #
                if l != 1:
                    # The final line
                    if l == length:
                        return (' ' * 4, '\"', '\"]\n')
                    # Not the end
                    else:
                        return (' ' * 4, '\"', '\", \\\n')
        # Stack the package list, one pkg a line
        def listPKG(apps, indent):
            arg = ''
            for app in apps:
                arg = arg + indent * 2 + app + ' \\\n'
            return(arg)
        # Script for apt installation
        def aptPKG(apts, indent, start):
            start = start +'apt-get update -qq \\\n' + indent + '&& apt-get install -y -q --no-install-recommends \\\n'
            indent = " " * 4
            arg = listPKG(apts, indent)
            arg = arg + indent + '&& apt-get clean \\\n' + indent + '&& rm -rf /var/lib/apt/lists/*'
            return (start, arg)
        # Script for tarball installation
        def tarPKG(tar, indent, start):
            start = '{start}mkdir -p {dist} \\\n'.format(start = start, dist = tar['dist'])
            indent = " " * 4
            arg = '{indent}&& curl -fSL --retry 5 {src} | tar -xz -C {dist} --strip-components 1'.format(
                indent = indent,
                src = tar['src'],
                dist = tar['dist']
            )
            return (start, arg)
        # Script for zipfile installation
        def zipPKG(tar, indent, start):
            start = '{start}cd /tmp && mkdir -p {dist} \\\n'.format(start = start, dist = tar['dist'])
            indent = " " * 4
            arg = '{indent}&& curl -fSL --retry 5 {src} -o tmp.zip && unzip tmp.zip -d {dist} && rm tmp.zip'.format(
                indent = indent,
                src = tar['src'],
                dist = tar['dist']
            )
            return (start, arg)
        # Script for making software from git repo
        def gitMAKE(git_make, indent, start):
            start = '{start}mkdir -p {build} \\\n'.format(start = start, build = git_make['build'])
            indent = " " * 4
            arg = '{indent}&& git clone {remote_src} {local_src} \\\n'.format(
                indent = indent,
                remote_src = git_make['remote_src'],
                local_src = git_make['local_src']
                )
            arg = arg + '{indent}&& cd {build} && dist={dist} \\\n'.format(
                indent = indent,
                build = git_make['build'],
                dist = git_make['dist']
                )
            arg = arg + '{indent}&& cmake {cmake} \\\n'.format(
                indent = indent,
                cmake = git_make['cmake']
            )
            arg = arg + '{indent}&& make {make} \\\n'.format(
                indent = indent,
                make = git_make['make']
            )
            arg = arg + '{indent}&& cd {installation} && make install 2>&1'.format(
                indent = indent,
                installation = git_make['installation']
            )
            return (start, arg)
        # Script for building software from git repo
        def gitBUILD(git_build, indent, start):
            start = '{start}git clone {remote_src} {local_src} \\\n'.format(
                start = start,
                remote_src = git_build['remote_src'],
                local_src = git_build['local_src'])
            indent = " " * 4
            arg = '{indent}&& cd {local_src} \\\n'.format(
                indent = indent,
                local_src = git_build['local_src']
            )
            arg = arg + '{indent}&& ./configure \\\n'.format(
                indent = indent
            )
            arg = arg + '{indent}&& ./build'.format(
                indent = indent
            )
            return (start, arg)
        # Script for conda installation (activate radioconda, then install)
        def condaPKG(conda, indent, start):
            start = start + 'bash -c \"source activate radioconda \\\n' +  indent  + '&& conda install -y  \\\n'
            indent = " " * 4
            arg = listPKG(conda, indent) + indent * 2 + '\"'
            return (start, arg)
        # Script for pip installation (activate radioconda, then install)
        def pipPKG(pip, indent, start):
            start = start + 'bash -c \"source activate radioconda \\\n' +  indent  + '&& pip install --no-cache-dir  \\\n'
            indent = " " * 4
            arg = listPKG(pip, indent) + indent * 2 + '\"'
            return (start, arg)
        """
        Compose the scripts, just expose mkDockfile
        :param head: config the build step. FROM, RUN, COPY, etc.
        :param scr: scripts for the step
        """
        def mkSCR(self, head, scr):
            args = scr
            # Point to the first line
            l = 1
            # append the Dockfile
            with open(self.dist, 'a') as f:
                # If the args in a dictionary
                if isinstance(args, dict):
                    # 'FROM' step, set base image
                    if head == "FROM ":
                        # Final format
                        txt = '{head}{base}:{tag}\n'.format(
                            head = head,
                            base = args['base'],
                            tag = args['tag']
                        )
                        f.write(txt)
                    # except for FROM
                    else:
                        length = len(args.items())
                        for arg, val in args.items():
                            # Formating the line
                            indent, start, end = identifyLine(l, length, head)
                            # For ARG step, to set empty ARG, or get ARG passed from outside command
                            if len(val) == 0 and head == "ARG ":
                                    val = ""
                            # For other steps, set variables like VAL="value"
                            else:
                                val = "=\"{val}\"".format(val = val)
                            # Final format
                            txt = '{indent}{start}{arg}{val}{end}'.format(
                                indent = indent,
                                start = start,
                                arg = arg,
                                val = val,
                                end = end)
                            f.write(txt)
                            # Point to next line
                            l += 1
                # If args is a list
                elif isinstance(args, list):
                    # Check how many apps gonna install
                    length = len(args)
                    for arg in args:
                        # Formating the line
                        if head == 'ENTRYPOINT ':
                            indent, start, end = identifyEntryLine(l, length, head)
                        else:
                            indent, start, end = identifyLine(l, length, head)
                        #
                        if head == 'RUN ' and l != 1:
                            if arg.startswith('*'):
                                start = start + '   '
                                arg = arg.replace('*', '', 2)
                            else:
                                start = start + '&& '
                        #
                        if head == 'RUN --mount=type=bind,':
                            try:
                                BIND_COPY
                            except NameError:
                                BIND_COPY = 0
                            bind_file = self.bind[BIND_COPY]
                            indent = ''
                            start = '{head}from={image}:{tag},target={target},source={dist} \\\n'.format(
                                head = head,
                                image = bind_file['image'],
                                tag = bind_file['tag'],
                                target = bind_file['target'],
                                dist = bind_file['dist']
                            )
                            arg = 'mkdir -p {dist} && cp -rf {target}/* {dist}'.format(
                                target = bind_file['target'],
                                dist = bind_file['dist']
                            )
                            end = '\n'
                            BIND_COPY += 1
                        #
                        if head == 'COPY ':
                            try:
                                COPY
                            except NameError:
                                COPY = 0
                            copy_file = self.copy[COPY]
                            indent = ''
                            start = '{head}{src} {dist}'.format(
                                head = head,
                                src = copy_file['src'],
                                dist = copy_file['dist']
                            )
                            arg = ''
                            end = '\n'
                            COPY += 1
                        #
                        if arg == 'APT_PKG':
                            try:
                                APT_PKG
                            except NameError:
                                APT_PKG = 0
                            start, arg = aptPKG(self.apts[APT_PKG], indent, start)
                            APT_PKG += 1
                        #
                        if arg == 'TAR_PKG':
                            try:
                                TAR_PKG
                            except NameError:
                                TAR_PKG = 0
                            start, arg = tarPKG(self.tar[TAR_PKG], indent, start)
                            TAR_PKG += 1
                        #
                        if arg == 'ZIP_PKG':
                            try:
                                ZIP_PKG
                            except NameError:
                                ZIP_PKG = 0
                            start, arg = zipPKG(self.zip[ZIP_PKG], indent, start)
                            ZIP_PKG += 1
                        #
                        if arg == 'GIT_MAKE':
                            try:
                                GIT_MAKE
                            except NameError:
                                GIT_MAKE = 0
                            start, arg = gitMAKE(self.git_make[GIT_MAKE], indent, start)
                            GIT_MAKE += 1
                        #
                        if arg == 'GIT_BUILD':
                            try:
                                GIT_BUILD
                            except NameError:
                                GIT_BUILD = 0
                            start, arg = gitBUILD(self.git_build[GIT_BUILD], indent, start)
                            GIT_BUILD += 1
                        #
                        if arg == 'CONDA_PKG':
                            try:
                                CONDA_PKG
                            except NameError:
                                CONDA_PKG = 0
                            start, arg = condaPKG(self.conda[CONDA_PKG], indent, start)
                            CONDA_PKG += 1
                        #
                        if arg == 'PIP_PKG':
                            try:
                                PIP_PKG
                            except NameError:
                                PIP_PKG = 0
                            start, arg = pipPKG(self.pip[PIP_PKG], indent, start)
                            PIP_PKG += 1
                        # Final format
                        txt = '{indent}{start}{arg}{end}'.format(
                                                                indent = indent,
                                                                start = start,
                                                                arg = arg,
                                                                end = end)
                        f.write(txt)
                        l += 1
                # if args is a string
                elif isinstance(args, str):
                    # Just one line for string
                    l = length = 1
                    arg = args
                    # Formating the line
                    indent, start, end = identifyLine(l, length, head)
                    # Final format
                    txt = '{indent}{start}{arg}{end}'.format(
                                                            indent = indent,
                                                            start = start,
                                                            arg = arg,
                                                            end = end)
                    f.write(txt)
                    l += 1
            f.close()
        """Write the Dockerfile"""
        with open(self.dist, 'w') as f:
            f.write('# radiodocker_{base} \n'.format(base = self.base))
            f.write('# build from {base}:{tag} \n'.format(
                base = self.steps['FROM ']['base'],
                tag = self.steps['FROM ']['tag'],
                ))
        f.close()
        for head, scr in self.steps.items():
            mkSCR(self, head, scr)

class buildIMAGE:
    """
    Build the docker image.
    :param conf_path:
    :param dist:
    :param base:
    :param args:
    :param log_dir: preserved (WIP)
    """
    def __init__(self, conf_path, dist, base, args, log_dir = ''):
        self.config = DockerConfig(conf_path, dist, base)
        self.short_base = base
        self.base = 'radiolab_{base}'.format(
            base = base,
        )
        self.tag = 'radiolab_{base}:{tag}'.format(
            base = base,
            tag = datetime.datetime.now().strftime('%Y%m%d')

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
    # Construct the build command
    # we didn't use docker-py api here, 'cause of output streaming and DOCKER_BUILDKIT support
    # the image will be temperally named radiolab_tmp:{base}
    def buildCommand(self):
        build_args = ' '.join(str(arg) for arg in ['--build-arg {}={}'.format(var, val) for var, val in self.args.items()])
        parent_dir = op.dirname(op.dirname(op.expanduser(self.dist)))
        docker_buildkit = 'docker build {args} --tag {tag} -f {dockerfile} {build_locate}'.format(
                tag = 'radiolab_tmp:{base}'.format(base = self.short_base),
                args = '{args}'.format(args = build_args),
                dockerfile = self.dist,
                build_locate = parent_dir)
        return docker_buildkit
    # Run the build command and stream the output
    # TODO how to log the streaming output?
    def build(self):
        # pattern = r'\x1B\[(([0-9]{1,2})?(;)?([0-9]{1,2})?)?[m,K,H,f,J]'
        os.environ["DOCKER_BUILDKIT"] = "1"
        # if self.loggin == 1:
        #     try:
        #         log_file = open(self.log_path, 'w')
        #         log_file.close()
        #     except:
        #         self.loggin = 0
        #         # log_file.write(re.sub(pattern, '', value) + "\n")
        #
        # Invoke Dockerconfig class mkDockerfile method
        self.config.mkDockerfile()
        # build command
        docker_buildkit = self.buildCommand()
        # Build!
        streamProcess(docker_buildkit)
        # name to image to its true name radiolab_{base}:{tag}, but preseve the tmp tag
        streamProcess('docker image tag radiolab_tmp:{base} {tag}'.format(tag = self.tag, base = self.short_base))

def buildSeq(build_seq_config, base, tag):
    """
    Return the sequence (dependence) of the images.
    :param build_seq_config: the path to the sequence config file.
    :param base: the target base name.
    :param: tag: the target tag.
    :return a dict {base:[tag]} with the lowest dependent image first and the target at the end.
    """
    import json
    seq = {base : [tag]}
    stage = seq
    dep = {'none' : 'none'}
    while dep:
        dep = dict()
        for img in stage.keys():
            with open(build_seq_config, 'r') as f:
                img_list = json.load(f)[img]['dep']
                for base, tag in img_list.items():
                    if base not in dep.keys():
                        dep[base] = [tag]
                    elif tag not in dep[base]:
                        multi_tag = dep[base]
                        multi_tag.append(tag)
                        dep[base] = multi_tag
            f.close()
        stage = dep
        seq = {**dep, **seq}
    return seq

def buildCMD(arguments):
    """
    """
    import sys
    import time
    import datetime
    import os.path as op
    import pkg_resources
    import shutil
    from os import makedirs
    from radiolabdocker.CheckStat import checkImageStat
    seq_path = pkg_resources.resource_filename('radiolabdocker', '/config/radiolab_build_config/radiolab_build_seq.json')
    conf_path = pkg_resources.resource_filename('radiolabdocker', '/config/radiolab_build_config/radiolab_img_config.json')
    base = arguments.base.split(':')
    df_dir = op.expanduser(arguments.dockerfile_dir)
    parent = op.dirname(df_dir)
    if not os.path.exists(parent + '/config/bash_config'):
        os.makedirs(parent + '/config/bash_config')
    shutil.copy(pkg_resources.resource_filename('radiolabdocker', '/config/bash_config/bashrc'), parent + '/config/bash_config/bashrc')
    if hasattr(arguments, 'proxy'):
        args = {"ALL_PROXY": arguments.proxy}
    else:
        args = {"ALL_PROXY": ''}
    if arguments.rebuild in ['False', 'F']:
        rebuild = False
    elif arguments.rebuild in ['True', 'T']:
        rebuild = True
    else:
        sys.exit('error: \'--rebuild\' should be either \'Ture(T)\' or \'False(F)\'')
    if arguments.force_rebuild in ['False', 'F']:
        force_rebuild = False
    elif arguments.force_rebuild in ['True', 'T']:
        force_rebuild = True
    else:
        sys.exit('error: \'--force_rebuild\' should be either \'Ture(T)\' or \'False(F)\'')
    if len(base) == 2:
        base, tag = base
    elif len(base) == 1:
        base = base[0]
        tag = 'latest'
    else:
        sys.exit('errors in the given base name, should be \'base\' or \'base:tag\'')
    if not (tag == 'latest' or tag == datetime.datetime.now().strftime('%Y%m%d')):
        sys.exit('the tag should be \'latest\' or the current date in YYYYMMDD format.')
    _, base = base.split('_')
    exist, tags = checkImageStat('radiolab_' + base)
    if exist and tag in tags and not (rebuild or force_rebuild):
        sys.exit('radiolab_{base}:{tag} exist, no need to build.'.format(base = base, tag = tag))
    seq = buildSeq(seq_path, base, tag)
    target = base
    for base, tags in seq.items():
        for tag in tags:
            exist, img_tags = checkImageStat("radiolab_" + base)
            tag = int(tag) if tag != 'latest' else tag
            if exist:
                img_tags = [ t for t in img_tags]
                if tag == 'latest':
                    if force_rebuild or (base == target and rebuild):
                        tag = int(datetime.datetime.now().strftime('%Y%m%d'))
                else:
                    sys.exit("the tag {tag} for {base} is not valid, please check the build_seq.json file".format(tag = tag, base = base))
            if (base == target and not rebuild) or (base != target and exist and (tag in img_tags) and not force_rebuild):
                print('radiolab_{base}:{tag} exist, no need to build.'.format(base = base, tag = tag))
                break
            retry = -1
            while not exist or (tag not in img_tags) or (base == target and rebuild) or force_rebuild:
                retry += 1
                print('building radiolab_{base}:{tag}'.format(base = base, tag = tag))
                if retry > 0:
                    print('build attemt {retry}'.format(retry = retry))
                if not op.exists(df_dir):
                    makedirs(df_dir)
                buildIMAGE(conf_path, df_dir, base, args).build()
                exist, img_tags = checkImageStat('radiolab_tmp')
                if exist and (base in img_tags):
                    if 'latest' in img_tags:
                        streamProcess('docker image rm radiolab_{base}:latest'.format(base = base))
                        time.sleep(1)
                    streamProcess('docker image tag radiolab_tmp:{base} radiolab_{base}:latest'.format(base = base))
                    time.sleep(1)
                    streamProcess('docker image rm radiolab_tmp:{base}'.format(base = base))
                    time.sleep(1)
                    exist, img_tags = checkImageStat("radiolab_" + base)
                    break
                if retry > 4:
                    break


