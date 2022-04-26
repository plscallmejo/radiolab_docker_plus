class DockerConfig:
#
#
    def __init__(self, conf_path, base):
#
        import json
        import os.path as op
#
        with open(conf_path, 'r') as f:
            config = json.load(f)[base]
        f.close()
#
        self.base = base
        self.config = config
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
        try:
            self.apts = config['apt']
        except:
            pass
        try:
            self.tar = config['tar']
        except:
            pass
        try:
            self.zip = config['zip']
        except:
            pass
        try:
            self.conda = config['conda']
        except:
            pass
        try:
            self.pip = config['pip']
        except:
            pass
        try:
            self.bind = config['bind_file']
        except:
            pass
        try:
            self.copy = config['copy_file']
        except:
            pass
        try:
            self.git_make = config['git_make']
        except:
            pass
        try:
            self.git_build = config['git_build']
        except:
            pass
        self.dist = op.join(dist, "Dockerfile_" + base)
#
#
    def mkDockerfile(self):
        with open(self.dist, 'w') as f:
            f.write('# radiodocker_{base} \n'.format(base = self.base))
            f.write('# build from {base}:{tag} \n'.format(
                base = self.steps['FROM ']['base'],
                tag = self.steps['FROM ']['tag'],
                ))
        f.close()
        for head, scr in self.steps.items():
            self.mkSCR(head, scr)
#
    def mkSCR(self, head, scr):
        args = scr
        # first line
        l = 1
        #
        def identifyLine(l, length, head):
                if l == 1:
                    if l == length:
                        return ('', head, '\n')
                    else:
                        return ('', head, ' \\\n')
                #
                if l != 1:
                    if l == length:
                        return (' ' * 4, '', '\n')
                    else:
                        return (' ' * 4, '', ' \\\n')
                #
        def listPKG(apps, indent):
            arg = ''
            for app in apps:
                arg = arg + indent * 2 + app + ' \\\n'
            return(arg)
        #
        def aptPKG(apts, indent, start):
            start = start +'apt-get update -qq \\\n' + indent + '&& apt-get install -y -q --no-install-recommends \\\n'
            indent = " " * 4
            arg = listPKG(apts, indent)
            arg = arg + indent + '&& apt-get clean \\\n' + indent + '&& rm -rf /var/lib/apt/lists/*'
            return (start, arg)
        #
        def tarPKG(tar, indent, start):
            start = '{start}mkdir -p {dist} \\\n'.format(start = start, dist = tar['dist'])
            indent = " " * 4
            arg = '{indent}&& curl -fSL --retry 5 {src} | tar -xz -C {dist} --strip-components 1'.format(
                indent = indent,
                src = tar['src'],
                dist = tar['dist']
            )
            return (start, arg)
        #
        def zipPKG(tar, indent, start):
            start = '{start}cd /tmp && mkdir -p {dist} \\\n'.format(start = start, dist = tar['dist'])
            indent = " " * 4
            arg = '{indent}&& curl -fSL --retry 5 {src} -o tmp.zip && unzip tmp.zip -d {dist} && rm tmp.zip'.format(
                indent = indent,
                src = tar['src'],
                dist = tar['dist']
            )
            return (start, arg)
        #
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
        #
        def condaPKG(conda, indent, start):
            start = start + 'bash -c \"source activate radioconda \\\n' +  indent  + '&& conda install -y  \\\n'
            indent = " " * 4
            arg = listPKG(conda, indent) + indent * 2 + '\"'
            return (start, arg)
        #
        def pipPKG(pip, indent, start):
            start = start + 'bash -c \"source activate radioconda \\\n' +  indent  + '&& pip install --no-cache-dir  \\\n'
            indent = " " * 4
            arg = listPKG(pip, indent) + indent * 2 + '\"'
            return (start, arg)
        #
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
        #
        with open(self.dist, 'a') as f:
            if isinstance(args, dict):
                if head == "FROM ":
                    txt = '{head}{base}:{tag}\n'.format(
                        head = head,
                        base = args['base'],
                        tag = args['tag']
                    )
                    f.write(txt)
                else:
                    length = len(args.items())
                    for arg, val in args.items():
                        indent, start, end = identifyLine(l, length, head)
                        if len(val) == 0 and head == "ARG ":
                                val = ""
                        else:
                            val = "=\"{val}\"".format(val = val)
                        txt = '{indent}{start}{arg}{val}{end}'.format(
                            indent = indent,
                            start = start,
                            arg = arg,
                            val = val,
                            end = end)
                        f.write(txt)
                        l += 1
            elif isinstance(args, list):
                length = len(args)
                APT_PKG = 0
                TAR_PKG = 0
                ZIP_PKG = 0
                GIT_MAKE = 0
                GIT_BUILD = 0
                CONDA_PKG = 0
                PIP_PKG = 0
                BIND_COPY = 0
                COPY = 0
                for arg in args:
                    indent, start, end = identifyLine(l, length, head)
                    if head == 'RUN --mount=type=bind,':
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
                    if head == 'COPY ':
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
                    if head == 'RUN ' and l != 1:
                        if arg.startswith('*'):
                            start = start + '   '
                            arg = arg.replace('*', '', 2)
                        else:
                            start = start + '&& '
                    if arg == 'APT_PKG':
                        start, arg = aptPKG(self.apts[APT_PKG], indent, start)
                        APT_PKG += 1
                    if arg == 'TAR_PKG':
                        start, arg = tarPKG(self.tar[TAR_PKG], indent, start)
                        TAR_PKG += 1
                    if arg == 'ZIP_PKG':
                        start, arg = zipPKG(self.zip[ZIP_PKG], indent, start)
                        ZIP_PKG += 1
                    if arg == 'GIT_MAKE':
                        start, arg = gitMAKE(self.git_make[GIT_MAKE], indent, start)
                        GIT_MAKE += 1
                    if arg == 'GIT_BUILD':
                        start, arg = gitBUILD(self.git_build[GIT_BUILD], indent, start)
                        GIT_BUILD += 1
                    if arg == 'CONDA_PKG':
                        start, arg = condaPKG(self.conda[CONDA_PKG], indent, start)
                        CONDA_PKG += 1
                    if arg == 'PIP_PKG':
                        start, arg = pipPKG(self.pip[PIP_PKG], indent, start)
                        PIP_PKG += 1
                    txt = '{indent}{start}{arg}{end}'.format(
                                                            indent = indent,
                                                            start = start,
                                                            arg = arg,
                                                            end = end)
                    f.write(txt)
                    l += 1
            elif isinstance(args, str):
                    l = length = 1
                    indent, start, end = identifyLine(l, length, head)
                    arg = args
                    txt = '{indent}{start}{arg}{end}'.format(
                                                            indent = indent,
                                                            start = start,
                                                            arg = arg,
                                                            end = end)
                    f.write(txt)
                    l += 1
        f.close()