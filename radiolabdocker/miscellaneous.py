def streamProcess(CMD: str):
    """
    Stream the cmd running process.
    :param CMD: the cmd to execute.
    """
    from time import sleep
    import subprocess
    process = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE)
    while process.poll() is None:
        try:
            for line in iter(process.stdout.readline, b''):
                value = line.decode("utf-8").strip()
                if value:
                    print(value)
        except subprocess.CalledProcessError as e:
            print(f"{str(e)}")
        sleep(0.1)

def timerHMS(time):
    """
    Return convert min-second to hour:minute:second format.
    :param time: time in ms
    """
    hour = time // 3600
    minute = (time - 3600 * hour) // 60
    second = (time - 3600 * hour - 60 * minute) // 1
    return (hour, minute, second)
