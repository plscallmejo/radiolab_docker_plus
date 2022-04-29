import pty

class LocalShell:
    def __init__(self, cmd):
        self.cmd = cmd
    def run(self):
        pty.spawn(self.cmd)

shell = LocalShell('./run.sh')
shell.run()