def runpty(container_name: str):
    """
    Run the interactive shell of the given container.
    :param container_name: the container name.
    """
    import os
    import docker
    # import dockerpty
    from radiolabdocker.CheckStat import checkContainerStat
    client = docker.from_env()
    load_config = '-c "source /radiolabdocker/startup.sh"'
    exist, (status, id) = checkContainerStat(container_name)
    if exist:
        container = client.containers.get(id)
        if status == 'running':
            pass
        elif status == 'exited':
            container.start()
        os.system('docker exec -it {container_name} /bin/bash {load_config}'.
                format(container_name = container_name,
                       load_config = load_config))
        # dockerpty.exec_command(client.api, container.id, '/bin/bash')
    else:
        import sys
        sys.exit("error: the container {container_name} is not exist, please check the spelling or create it.".format(container_name = container_name))