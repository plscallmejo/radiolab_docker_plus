# Originally generated by: Neurodocker version 0.7.0+0.gdc97516.dirty
# Timestamp: 2021/01/21 15:32:09 UTC

# FROM nvidia/cudagl:9.1-runtime-ubuntu16.04
FROM ubuntu:16.04

# nvidia-container-runtime
# ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
# ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

USER root

ARG DEBIAN_FRONTEND="noninteractive"

ENV LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" 
RUN sed -i "s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list 
#    && echo "deb https://mirrors.aliyun.com/nvidia-cuda/ubuntu1604/x86_64/ ./" > /etc/apt/sources.list.d/cuda.list \
    
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           apt-utils \
           bzip2 \
           sudo \
           wget \
           curl \
           aria2 \
           locales \
           unzip \
    	   htop \
    	   bmon \
           apt-transport-https \
           ca-certificates \
    	   software-properties-common \
    	   python-software-properties \
           tmux \
           vim \
           firefox \
           bc \
           dc \
           file \
           libfontconfig1 \
           libfreetype6 \
           libgl1-mesa-dev \
           libgl1-mesa-dri \
           libglu1-mesa-dev \
           libgomp1 \
           libice6 \
           libxcursor1 \
           libxft2 \
           libxinerama1 \
           libxrandr2 \
           libxrender1 \
           libxt6 \
           libgomp1 \
           libxmu6 \
           libxt6 \
           perl \
           tcsh \
    && echo "deb https://cloud.r-project.org/bin/linux/ubuntu xenial-cran35/" >> /etc/apt/sources.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
    && apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           ed \
           gsl-bin \
           libglib2.0-0 \
           libglu1-mesa-dev \
           libglw1-mesa \
           libgomp1 \
           libjpeg62 \
           libnlopt-dev \
           libxm4 \
           netpbm \
           python3 \
           r-base \
           r-base-dev \
           tcsh \
           xfonts-base \
           xvfb \
    && curl -sSL --retry 5 -o /tmp/toinstall.deb http://mirrors.kernel.org/debian/pool/main/libx/libxp/libxp6_1.0.2-2_amd64.deb \
    && dpkg -i /tmp/toinstall.deb \
    && rm /tmp/toinstall.deb \
    && apt-get install -f \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && gsl2_path="$(find / -name 'libgsl.so.19' || printf '')" \
    && if [ -n "$gsl2_path" ]; then \
         ln -sfv "$gsl2_path" "$(dirname $gsl2_path)/libgsl.so.0"; \
    fi \
    && ldconfig \ 
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG="en_US.UTF-8" \
    && chmod 777 /opt && chmod a+s /opt 
    
RUN add-apt-repository ppa:max-c-lv/shadowsocks-libev -y \
    && apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
	    shadowsocks-libev \
	    build-essential \
	    autoconf \
	    libtool \
	    libssl-dev \
	    libpcre3-dev \
	    libc-ares-dev \
	    libev-dev \
	    asciidoc \
	    xmlto \
	    automake \
	    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 
RUN git clone https://github.com/shadowsocks/simple-obfs.git \
    && cd simple-obfs \
    && git submodule update --init --recursive \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    && rm -rf simple-obfs 
RUN git clone https://github.com/rofl0r/proxychains-ng.git \
    && cd proxychains-ng \
    && ./configure --prefix=/usr --sysconfdir=/etc \
    && make \
    && make install \
    && make install-config \
    && cd .. \
    && rm -rf proxychains-ng 
COPY ["content/proxychains.conf", "/etc/proxychains.conf"]
COPY ["content/shadowsocks.json", "/etc/shadowsocks.json"]

RUN mkdir -p /radiolabdocker \
    && chmod -R 777 /radiolabdocker && chmod a+s /radiolabdocker \
    && export RD_ENTRYPOINT="/radiolabdocker/startup.sh" \
    && if [ ! -f "$RD_ENTRYPOINT" ]; then \
         echo '#!/usr/bin/env bash' >> "$RD_ENTRYPOINT" \
    &&   echo 'set -e' >> "$RD_ENTRYPOINT" \
    &&   echo 'export USER="${USER:=`whoami`}"' >> "$RD_ENTRYPOINT"; \
    fi 
ENV RD_ENTRYPOINT="/radiolabdocker/startup.sh"
ENTRYPOINT ["/radiolabdocker/startup.sh"]

COPY ["content/fsl-6.0.4-centos7_64.tar.gz", "/tmp/"]
ENV FSLDIR="/opt/fsl-6.0.4" \
    PATH="/opt/fsl-6.0.4/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-6.0.4/bin/fsltclsh" \
    FSLWISH="/opt/fsl-6.0.4/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLMACHINELIST="" \
    FSLREMOTECALL="" \
    FSLGECUDAQ="cuda.q"
RUN echo "Installing FSL ..." \
    && `ss-local -c /etc/shadowsocks.json > /dev/null 2>&1 &` \
#    && proxychains4 curl -fsSL --retry 5 https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-6.0.4-centos7_64.tar.gz \
    && mkdir /opt/fsl-6.0.4 \
    && tar -xzvf /tmp/fsl-6.0.4-centos7_64.tar.gz -C /opt/fsl-6.0.4 --strip-components 1 \
    && echo 'Some packages in this Docker container are non-free' \
    && echo 'If you are considering commercial use of this container, please consult the relevant license:' \
    && echo 'https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence' \
    && echo "Installing FSL conda environment ..." \
    && proxychains4 bash /opt/fsl-6.0.4/etc/fslconf/fslpython_install.sh -f /opt/fsl-6.0.4 \
    && sed -i '$isource $FSLDIR/etc/fslconf/fsl.sh' $RD_ENTRYPOINT \
    && rm /tmp/fsl-6.0.4-centos7_64.tar.gz

COPY ["content/linux_openmp_64.tgz", "/tmp/linux_openmp_64.tgz"]
ENV PATH="/opt/afni-latest:$PATH" \
    AFNI_PLUGINPATH="/opt/afni-latest"
RUN echo "Installing AFNI ..." \
    && mkdir -p /opt/afni-latest \
#     && curl -fsSL --retry 5 https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz \
#     | tar -xz -C /opt/afni-latest --strip-components 1 \
    && tar -zxvf /tmp/linux_openmp_64.tgz -C /opt/afni-latest --strip-components 1 \
    && PATH=$PATH:/opt/afni-latest rPkgsInstall -pkgs ALL \
    && rm /tmp/linux_openmp_64.tgz

# ENV CONDA_DIR="/opt/miniconda-latest" \
#     PATH="/opt/miniconda-latest/bin:$PATH"
# RUN export PATH="/opt/miniconda-latest/bin:$PATH" \
#     && echo "Downloading Miniconda installer ..." \
#     && conda_installer="/tmp/miniconda.sh" \
#     && curl -fsSL --retry 5 -o "$conda_installer" https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#     && bash "$conda_installer" -b -p /opt/miniconda-latest \
#     && rm -f "$conda_installer" \
#     && conda update -yq -nbase conda \
#     && conda config --system --prepend channels conda-forge \
#     && conda config --system --set auto_update_conda false \
#     && conda config --system --set show_channel_urls true \
#     && sync && conda clean -y --all && sync 
# RUN conda install -y -q \
#            "numpy" \
#            "scipy" \
#            "pandas" \
#            "nilearn" \
#            "nipype" \
#            "matplotlib" \
#     && sync && conda clean -y --all && sync

COPY ["content/freesurfer-linux-centos7_x86_64-7.1.1.tar.gz", "/tmp/"]
COPY ["content/license.txt", "/tmp/"]
ENV FREESURFER_HOME="/opt/freesurfer-7.1.1" \
    PATH="/opt/freesurfer-7.1.1/bin:$PATH"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           qt5-default \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 
RUN echo "Installing FreeSurfer ..." \
    && mkdir -p /opt/freesurfer-7.1.1 \
#    && curl -fsSL --retry 5 ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.1.1/freesurfer-Linux-centos6_x86_64-stable-pub-v7.1.1.tar.gz \
    && tar -zxvf /tmp/freesurfer-linux-centos7_x86_64-7.1.1.tar.gz -C /opt/freesurfer-7.1.1 --strip-components 1 \
    && sed -i '$isource "/opt/freesurfer-7.1.1/SetUpFreeSurfer.sh"' "$RD_ENTRYPOINT" \
    && mv /tmp/license.txt /opt/freesurfer-7.1.1/ \
    && rm /tmp/freesurfer-linux-centos7_x86_64-7.1.1.tar.gz

COPY ["content/ants-Linux-centos6_x86_64-v2.3.4.tar.gz", "/tmp/ants-Linux-centos6_x86_64-v2.3.4.tar.gz"]
ENV ANTSPATH="/opt/ants-2.3.4" \
    PATH="/opt/ants-2.3.4:$PATH"
RUN echo "Installing ANTs ..." \
    && mkdir -p /opt/ants-2.3.4 \
#     && curl -fsSL --retry 5 https://dl.dropbox.com/s/1xfhydsf4t4qoxg/ants-Linux-centos6_x86_64-v2.3.1.tar.gz \
#     | tar -xz -C /opt/ants-2.3.1 --strip-components 1 \
    && tar -zxvf /tmp/ants-Linux-centos6_x86_64-v2.3.4.tar.gz -C /opt/ants-2.3.4 --strip-components 1 \
    && rm /tmp/ants-Linux-centos6_x86_64-v2.3.4.tar.gz

RUN rm /etc/proxychains.conf \
    && rm /etc/shadowsocks.json

COPY ["content/fsl_sub", "/opt/fsl-6.0.4/bin/fsl_sub"]
RUN chmod a+x /opt/fsl-6.0.4/bin/fsl_sub

RUN chmod 755 /radiolabdocker/startup.sh \
    && echo 'if [ -n "$1" ]; then "$@"; else /usr/bin/env bash; fi' >> $RD_ENTRYPOINT \
    && echo '{ \
    \n  "pkg_manager": "apt", \
    \n  "instructions": [ \
    \n    [ \
    \n      "base", \
    \n      "ubuntu:16.04" \
    \n    ], \
    \n    [ \
    \n      "fsl", \
    \n      { \
    \n        "version": "6.0.4" \
    \n      } \
    \n    ], \
    \n    [ \
    \n      "freesurfer", \
    \n      { \
    \n        "version": "7.1.1" \
    \n      } \
    \n    ], \
    \n    [ \
    \n      "ants", \
    \n      { \
    \n        "version": "2.3.4" \
    \n      } \
    \n    ], \
    \n    [ \
    \n      "afni", \
    \n      { \
    \n        "version": "latest", \
    \n        "install_r": "true", \
    \n        "install_r_pkgs": "true", \
    \n        "install_python3": "true" \
    \n      } \
    \n    ] \
    \n  ] \
    \n}' > /radiolabdocker/radiolabdocker_specs.json
