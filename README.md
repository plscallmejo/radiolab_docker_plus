## radiolab_docker plus

A fully upgraded version of radiolab_docker, the previous bash scripts for constructing, managing, and deploying a robust and reproducible neuroimage analysis environment, and are now re-written in python (puls for upgrade and for python), hence, compatible with linux and windows. Also, a `xpra` server with html5 frontend will be set up in docker for display, and no xvcsrv or other kind of xserver is needed (I would rather regard `xpra` as the os boundary breaker for radiolab_docker plus).

## Included softwares

* AFNI
* ANTs
* FSL
* Freesuefer
* convert3D
* dcm2niix
* dsistudio
* qsiprep
* miniconda (Radiolabconda environment with python3.8)

## TODOs

- [ ] Host network
- [ ] Clear build cache
- [ ] Port host x11

## Acknowledgements

The Dockerfile_OG was originally based on a Dockerfile generated by [neurodocker](https://github.com/ReproNim/neurodocker),
that is a great work!
