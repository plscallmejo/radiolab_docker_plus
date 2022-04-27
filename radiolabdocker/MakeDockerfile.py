import json
import os.path as op

class DockerConfig:
    """
    Make a Dockerfile according to the config file.
    :param conf_path: path to config file
    :param dist: path to Dockerfile, the Dockerfile will be renamed to Dockerfile_{base}
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
    """
    Write the Dockerfile
    """
    def mkDockerfile(self):
        # Check the current line, and set the (indent, start, end) for a line
        def __identifyLine__(l, length, head):
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
        def __identifyEntryLine__(l, length, head):
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
        def __listPKG__(apps, indent):
            arg = ''
            for app in apps:
                arg = arg + indent * 2 + app + ' \\\n'
            return(arg)
        # Script for apt installation
        def __aptPKG__(apts, indent, start):
            start = start +'apt-get update -qq \\\n' + indent + '&& apt-get install -y -q --no-install-recommends \\\n'
            indent = " " * 4
            arg = __listPKG__(apts, indent)
            arg = arg + indent + '&& apt-get clean \\\n' + indent + '&& rm -rf /var/lib/apt/lists/*'
            return (start, arg)
        # Script for tarball installation
        def __tarPKG__(tar, indent, start):
            start = '{start}mkdir -p {dist} \\\n'.format(start = start, dist = tar['dist'])
            indent = " " * 4
            arg = '{indent}&& curl -fSL --retry 5 {src} | tar -xz -C {dist} --strip-components 1'.format(
                indent = indent,
                src = tar['src'],
                dist = tar['dist']
            )
            return (start, arg)
        # Script for zipfile installation
        def __zipPKG__(tar, indent, start):
            start = '{start}cd /tmp && mkdir -p {dist} \\\n'.format(start = start, dist = tar['dist'])
            indent = " " * 4
            arg = '{indent}&& curl -fSL --retry 5 {src} -o tmp.zip && unzip tmp.zip -d {dist} && rm tmp.zip'.format(
                indent = indent,
                src = tar['src'],
                dist = tar['dist']
            )
            return (start, arg)
        # Script for making software from git repo
        def __gitMAKE__(git_make, indent, start):
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
        def __gitBUILD__(git_build, indent, start):
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
        def __condaPKG__(conda, indent, start):
            start = start + 'bash -c \"source activate radioconda \\\n' +  indent  + '&& conda install -y  \\\n'
            indent = " " * 4
            arg = __listPKG__(conda, indent) + indent * 2 + '\"'
            return (start, arg)
        # Script for pip installation (activate radioconda, then install)
        def __pipPKG__(pip, indent, start):
            start = start + 'bash -c \"source activate radioconda \\\n' +  indent  + '&& pip install --no-cache-dir  \\\n'
            indent = " " * 4
            arg = __listPKG__(pip, indent) + indent * 2 + '\"'
            return (start, arg)
        """
        Compose the scripts, just expose mkDockfile
        :param head: config the build step. FROM, RUN, COPY, etc.
        :param scr: scripts for the step
        """
        def __mkSCR__(self, head, scr):
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
                            indent, start, end = __identifyLine__(l, length, head)
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
                            indent, start, end = __identifyEntryLine__(l, length, head)
                        else:
                            indent, start, end = __identifyLine__(l, length, head)
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
                            start, arg = __aptPKG__(self.apts[APT_PKG], indent, start)
                            APT_PKG += 1
                        #
                        if arg == 'TAR_PKG':
                            try:
                                TAR_PKG
                            except NameError:
                                TAR_PKG = 0
                            start, arg = __tarPKG__(self.tar[TAR_PKG], indent, start)
                            TAR_PKG += 1
                        #
                        if arg == 'ZIP_PKG':
                            try:
                                ZIP_PKG
                            except NameError:
                                ZIP_PKG = 0
                            start, arg = __zipPKG__(self.zip[ZIP_PKG], indent, start)
                            ZIP_PKG += 1
                        #
                        if arg == 'GIT_MAKE':
                            try:
                                GIT_MAKE
                            except NameError:
                                GIT_MAKE = 0
                            start, arg = __gitMAKE__(self.git_make[GIT_MAKE], indent, start)
                            GIT_MAKE += 1
                        #
                        if arg == 'GIT_BUILD':
                            try:
                                GIT_BUILD
                            except NameError:
                                GIT_BUILD = 0
                            start, arg = __gitBUILD__(self.git_build[GIT_BUILD], indent, start)
                            GIT_BUILD += 1
                        #
                        if arg == 'CONDA_PKG':
                            try:
                                CONDA_PKG
                            except NameError:
                                CONDA_PKG = 0
                            start, arg = __condaPKG__(self.conda[CONDA_PKG], indent, start)
                            CONDA_PKG += 1
                        #
                        if arg == 'PIP_PKG':
                            try:
                                PIP_PKG
                            except NameError:
                                PIP_PKG = 0
                            start, arg = __pipPKG__(self.pip[PIP_PKG], indent, start)
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
                    indent, start, end = __identifyLine__(l, length, head)
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
            __mkSCR__(self, head, scr)