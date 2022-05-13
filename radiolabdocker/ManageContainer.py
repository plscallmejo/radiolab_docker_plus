def startContainer(container_name):
    '''
    '''
    import sys
    import docker
    from radiolabdocker.CheckStat import checkContainerStat
    exist, (status, id) = checkContainerStat(container_name)
    if not exist:
        sys.exit('the container {container} dose not exist, please check the spell or create it.'.format(container = container_name))
    if status == 'created' or status == 'exited':
        print('bringing up the container {container} ...'.format(container = container_name), end = '')
        client = docker.from_env()
        client.containers.get(id).start()
        print('done.')
    elif status == 'running':
        sys.exit('the container {container} is running.'.format(container = container_name))
    elif status == 'paused':
        sys.exit('the container {container} paused, unpause it instead.'.format(container = container_name))

def stopContainer(container_name):
    '''
    '''
    import sys
    import docker
    from radiolabdocker.CheckStat import checkContainerStat
    exist, (status, id) = checkContainerStat(container_name)
    if not exist:
        sys.exit('the container {container} dose not exist, please check the spell or create it.'.format(container = container_name))
    if status == 'running' or status == 'paused':
        print('exiting the container {container} ...'.format(container = container_name), end = '')
        client = docker.from_env()
        client.containers.get(id).stop()
        print('done.')
    elif status == 'exited':
        sys.exit('the container {container} exited.'.format(container = container_name))

def pauseContainer(container_name):
    '''
    '''
    import sys
    import docker
    from radiolabdocker.CheckStat import checkContainerStat
    exist, (status, id) = checkContainerStat(container_name)
    if not exist:
        sys.exit('the container {container} dose not exist, please check the spell or create it.'.format(container = container_name))
    if status == 'running':
        print('pausing the container {container} ...'.format(container = container_name), end = '')
        client = docker.from_env()
        client.containers.get(id).pause()
        print('done.')
    elif status == 'paused':
        sys.exit('the container {container} paused.'.format(container = container_name))
    elif status == 'exited':
        sys.exit('can not pause the exited container {container}.'.format(container = container_name))

def unpauseContainer(container_name):
    '''
    '''
    import sys
    import docker
    from radiolabdocker.CheckStat import checkContainerStat
    exist, (status, id) = checkContainerStat(container_name)
    if not exist:
        sys.exit('the container {container} dose not exist, please check the spell or create it.'.format(container = container_name))
    if status == 'paused':
        print('unpausing the container {container} ...'.format(container = container_name), end = '')
        client = docker.from_env()
        client.containers.get(id).unpause()
        print('done.')
    elif status == 'running':
        sys.exit('the container {container} is running.'.format(container = container_name))
    elif status == 'exited':
        sys.exit('can not unpause the exited container {container}.'.format(container = container_name))

def removeContainer(container_name, force):
    '''
    '''
    import sys
    import docker
    from radiolabdocker.CheckStat import checkContainerStat
    exist, (_, id) = checkContainerStat(container_name)
    if not exist:
        sys.exit('the container {container} dose not exist, please check the spell or create it.'.format(container = container_name))
    print('removing the container {container} ... '.format(container = container_name), end = '')
    client = docker.from_env()
    client.containers.get(id).remove(force = force)
    print('done.')
