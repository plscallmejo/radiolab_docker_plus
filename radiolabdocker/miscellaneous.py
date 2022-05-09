import sys
import threading

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

class asyncRunner(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None
    #
    def run(self):
        if self._target is None:
            return  # could alternatively raise an exception, depends on the use case
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as exc:
            print(f'{type(exc).__name__}: {exc}', file=sys.stderr)  # properly handle the exception
    #
    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self.result

def estGzipDecompress(filename):
    import os
    import zlib
    import struct
    from io import SEEK_END
    # from https://stackoverflow.com/a/68939759
    raw = open(filename, 'rb')
    # whole file compressed size
    file_size = os.fstat(raw.fileno()).st_size
    # take 1M compressed sample
    raw = open(filename, 'rb')
    sample = raw.read(1024 * 1024)
    # decompress the sample
    d_obj = zlib.decompressobj(16+zlib.MAX_WBITS)
    dsample = d_obj.decompress(sample)
    # calculate the unadjusted size
    estimate = round(file_size * len(dsample) / len(sample))
    # read the 32 lsb (I dont understand)
    raw.seek(-4, SEEK_END)
    lsb = struct.unpack('I', raw.read(4))[0]
    mask = ~0xFFFFFFFF
    # calculate the adj. est. size
    adjusted_estimate = (estimate & mask) | lsb
    raw.close()
    return adjusted_estimate
