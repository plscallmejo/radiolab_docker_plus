def checkContainerStat(check_container: str):
    """
    Return the existance and running status of a given container name.
    :param: check_container: the name of a contariner.
    :return: (existance (bool), running status (Running, Exit, None if not exist))
    """
    import docker
    client = docker.from_env()
    container_ls = client.containers.list(all = True)
    container_stat = {container.name: [container.status, container.id] for container in container_ls}
    contariner_name = container_stat.keys()
    # Check existance and status
    if check_container in contariner_name:
        exist = True
        stat = container_stat[check_container]
    else:
        exist = False
        stat = None, None
    #
    return(exist, stat)

def checkImageStat(check_img: str):
    """
    Return the existance and tags of a given image name.
    :param: check_image: the name of a image.
    :return: (existance (bool), tags (dict))
    """
    import docker
    client = docker.from_env()
    image_ls = client.images.list()
    img_tags = { img.tags[0].split(':')[0]:[ tag.split(':')[1] for tag in img.tags ] for img in image_ls }
    img_name = img_tags.keys()
    # Check existance and tags
    if check_img in img_name:
        exist = True
        tags = img_tags[check_img]
    else:
        exist = False
        tags = None
    #
    return (exist, tags)

def checkVolumeStat(volume):
    '''
    '''
    import docker
    client = docker.from_env()
    volumes_ls = client.volumes.list()
    volumes = [vol.name for vol in volumes_ls]
    if volume in volumes:
        return True
    else:
        return False