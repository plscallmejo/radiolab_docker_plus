def saveImage(path, base, tag = 'latest'):
    """
    Save the image to tar.gz archive.
    :param path: the saving path, the tarball will be named to radiolab_xxx#[build_date_tag]_[save_date].tar.gz.
    :param base: the image base name.
    :param tag: specified the date tag (default: 'latest')
    """
    import sys
    import gzip
    import docker
    import datetime
    import os.path as op
    from time import perf_counter
    from radiolabdocker.CheckStat import checkImageStat
    from radiolabdocker.miscellaneous import timerHMS, streamProcess
    # modified from https://github.com/docker/docker-py/issues/1352#issuecomment-266853096
    # Set up client, and specified the time-out to 30min in case larger image
    client = docker.from_env(timeout = 1800)
    # If tag given other than 'latest' convert it to int
    tag = int(tag) if tag != 'latest' else tag
    # Check image stat
    exist, tags = checkImageStat(base)
    # If 'latest', set tag to latest build
    if exist:
        tags = [ int(t) for t in tags if t != 'latest']
        if tag == 'latest':
            tag = str(max(tags))
        elif tag in tags:
            tag = str(tag)
        else:
            sys.exit('the tag {tag} is not valid'.format(tag = tag))
        # Get current date
        date = datetime.datetime.now().strftime('%Y%m%d')
        # Set tarball name
        tarball = op.abspath(op.expanduser('{path}/{base}#{tag}_{date}.tar.gz'.format(
            path = path,
            base = base,
            tag = tag,
            date = date)))
        # Get image
        image = client.images.get('{}:{}'.format(base, tag))
        print('getting data from {}:{} ...'.format(base, tag))
        # Timer 1
        tl1 = perf_counter()
        # Set chunk size to 32768 for stability
        chunk_size = 32768
        # Estimate the size with VirtualSize, the actual size would be large
        image_size = image.attrs['VirtualSize']
        # Get Chunks from generator
        chunks = image.save(chunk_size, named = '{}:{}'.format(base, tag))
        # Just est. iters
        iters = round(image_size / chunk_size)
        # Timer 2
        tl2 = perf_counter()
        # Display loading time
        tl = tl2 - tl1
        hour, minute, second = timerHMS(tl)
        print('\rconsumed %02d:%02d:%02d' % (hour, minute, second))
        print('saving {}:{} to {}'.format(base, tag, tarball))
        # Gzip it
        with gzip.open(tarball, 'wb') as tf:
            # The first chunk
            i = 1
            # Reset gzip time
            t = 0
            last = 0
            t1_next = perf_counter()
            hour = 0
            minute = 0
            second = 0
            for chunk in chunks:
                # Timer 3
                t1_last = t1_next
                t1_next = perf_counter()
                gap = t1_next - t1_last
                t1 = t1_next
                last = last + gap
                # Accumulate time
                _, _, last_s = timerHMS(last)
                # Progress bar
                per = round(i / iters * 100)
                # Subpress the percentage to 100%
                per = 100 if per > 100 else per
                num = per // 2
                subpress_output = tf.write(chunk)
                if per < 3:
                    process = "\r[%3s%%]: |%-50s| estimating ..." % (per, '|' * num)
                else:
                    process = "\r[%3s%%]: |%-50s| est. %02d:%02d:%02d " % (per, '|' * num, hour, minute, second)
                print(process, end='', flush=True)
                # Timer 4
                t2 = perf_counter()
                # Calcu time consumed, est time left.
                t = t + (t2 - t1)
                per_iter = t / i
                # is acuumulate time > 0.5s, refresh the est.
                if last_s > 0.5:
                    last = 0
                    # In case strange thing happen, if i > iters, cause the image size is just an est.
                    # that smaller than the actual size
                    est_left = (0 if (iters - i) < 0 else (iters - i)) * per_iter
                    hour, minute, second = timerHMS(est_left)
                # Next Chunk
                i += 1
            # Calculate the total time consumed
            hour, minute, second = timerHMS(t + tl)
            print('\r\nDone. Total time consumed %02d:%02d:%02d' % (hour, minute, second))
            tf.close()

def saveCMD(path, image):
    """
    """
    import sys
    base = image.split(':')
    if len(base) == 2:
        base, tag = base
    elif len(base) == 1:
        base = base[0]
        tag = 'latest'
    else:
        sys.exit('errors in the given base name, should be \'base\' or \'base:tag\'')
    saveImage(path = path, base = base, tag = tag)

def loadImage(tarball):
    """
    """
    import re
    import gzip
    import subprocess
    import os.path as op
    from time import sleep
    from radiolabdocker.CheckStat import checkImageStat
    from radiolabdocker.miscellaneous import streamProcess
    tarball = op.abspath(op.expanduser(tarball))
    base = re.sub(r'(radiolab_[a-z]+)#[0-9]*_[0-9]*.tar.gz', r'\1', op.basename(tarball))
    gz = gzip.open(tarball, 'rb')
    print('loading {tarball} (may take a long while for large image)'.format(tarball = tarball))
    process = subprocess.Popen('docker load', shell=True, stdout=subprocess.PIPE, stdin = gz)
    #
    while process.poll() is None:
        try:
            for line in iter(process.stdout.readline, b''):
                value = line.decode("utf-8").strip()
                if value:
                    print(value)
        except subprocess.CalledProcessError as e:
            print(f"{str(e)}")
        sleep(0.1)
    #
    exist, tags = checkImageStat(base)
    #
    if exist:
        tags = [ int(t) for t in tags if t != 'latest']
        latest_tag = str(max(tags))
        #
    streamProcess('docker image tag {base}:{latest_tag} {base}:latest'.format(base = base, latest_tag = latest_tag))

def loadCMD(tarball):
    loadImage(tarball)

