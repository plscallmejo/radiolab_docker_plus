import subprocess
from time import sleep

def streamProcess(CMD: str):
    """
    Stream the cmd running process.
    :param CMD: the cmd to execute.
    """
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

import pty
class LocalShell:
    def __init__(self, cmd):
        self.cmd = cmd
    def run(self):
        pty.spawn(self.cmd)
