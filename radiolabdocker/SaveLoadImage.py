def saveImage(path, base, tag = 'latest'):
    """
    Save the image to tar.gz archive.
    :param path: the saving path, the tarball will be named to radiolab_xxx#[build_date_tag]_[save_date].tar.gz.
    :param base: the image base name.
    :param tag: specified the date tag (default: 'latest')
    """
    import os
    import sys
    import gzip
    import docker
    import datetime
    import os.path as op
    from time import perf_counter
    from radiolabdocker.CheckStat import checkImageStat
    from radiolabdocker.miscellaneous import timerHMS, asyncRunner
    # modified from https://github.com/docker/docker-py/issues/1352#issuecomment-266853096
    # Set up client, and specified the time-out to 30min in case larger image
    client = docker.from_env(timeout = 1800)
    # If tag given other than 'latest' convert it to int
    tag = int(tag) if tag != 'latest' else tag
    # Check image stat
    exist, tags = checkImageStat(base)
    # If not exist
    if (not exist) and (tag not in tags):
        sys.exit('the image {base}:{tag} is not exist.'.format(base = base, tag = tag))
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
        print('getting data from {}:{} ... '.format(base, tag))
        print('(do not interrupt, it occupies memory that can not recorver for a moment)')
        # Timer 1
        tl1 = perf_counter()
        # Set chunk size to 32768 for stability
        chunk_size = 32768
        # Estimate the size with VirtualSize, the actual size would be large
        image_size = image.attrs['VirtualSize']
        # Just est. iters
        iters = round(image_size / chunk_size)
        # Get Chunks from generator
        # Use Thread module for async run the image.save and the timer
        job = asyncRunner(target = image.save, kwargs={'named':'{}:{}'.format(base, tag)})
        # Run the image save
        job.start()
        # chunks = image.save(chunk_size, named = '{}:{}'.format(base, tag))
        while job.is_alive():
            # Timer 2
            tl2 = perf_counter()
            # Display loading time
            tl = tl2 - tl1
            hour, minute, second = timerHMS(tl)
            print('\rconsumed %02d:%02d:%02d' % (hour, minute, second), end = '', flush = True)
        # Gether the result
        chunks = job.join()
        print('\nsaving {}:{} to {}'.format(base, tag, tarball))
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
            term_width = os.get_terminal_size().columns
            if term_width >= 79:
                bar_width = 50
            else:
                bar_width = term_width - 28
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
                _ = tf.write(chunk)
                # do not display ets. on the first 3%
                if per < 3:
                    proc = "\r[%3s%%]: |%-{bar_width}s| estimating ...".format(bar_width = bar_width) % (per, '|' * num)
                elif per == 100 and (i / iters) > 1:
                    proc = "\r[%3s%%]: |%-{bar_width}s| almost ...    ".format(bar_width = bar_width) % (per, '|' * num)
                else:
                    proc = "\r[%3s%%]: |%-{bar_width}s| est. %02d:%02d:%02d ".format(bar_width = bar_width) % (per, '|' * num, hour, minute, second)
                print(proc, end='', flush=True)
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
            print("\r[%3s%%]: |%-{bar_width}s| done.         ".format(bar_width = bar_width) % (per, '|' * num), end = '\n', flush = True)
            print('\rtotal time consumed %02d:%02d:%02d' % (hour, minute, second))
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

def loadImage(tarball: str):
    """
    Load the image in tar.gz format that previously save by `docker save` and piped to gzip for compression.
    :param tarball: the path to the tar.gz archive.
    """
    import re
    import gzip
    import subprocess
    import os
    import sys
    import os.path as op
    from time import sleep, perf_counter
    from radiolabdocker.CheckStat import checkImageStat
    from radiolabdocker.miscellaneous import streamProcess, estGzipDecompress, timerHMS
    tarball = op.abspath(op.expanduser(tarball))
    if not op.exists(tarball):
        sys.exit('the {tarball} is not exist'.format(tarball = tarball))
    # Get the base name, assuming named as it save
    # TODO test the naming validility of a gzip tar
    base = re.sub(r'(radiolab_[a-z]+)#[0-9]*_[0-9]*.tar.gz', r'\1', op.basename(tarball))
    # Loading
    print('loading {tarball}.'.format(tarball = tarball))
    # Setup a cmd pipe subprocess
    process = subprocess.Popen('docker load', shell=True, stdout=subprocess.PIPE, stdin = subprocess.PIPE)
    # Get the estimate size of the gzip tarball
    adjusted_estimate = estGzipDecompress(tarball)
    # Calculate 1% size for smoother loading display (just a trick)
    percentage_estimate = adjusted_estimate / 100
    # Timer
    t = 0
    last = 0
    t1_next = perf_counter()
    hour = 0
    minute = 0
    second = 0
    # avoid divided by zero error
    total_chunk = 1
    # Auto suit the terminal width
    # Get terminal width
    term_width = os.get_terminal_size().columns
    if term_width >= 79:
        bar_width = 50
    else:
        bar_width = term_width - 28
    # Open a gzip
    gz = gzip.open(tarball, 'rb')
    # chunk_size for 2mb by default
    chunk_size = 2
    chunk_size = chunk_size * 1024 * 1024
    # Read the file chunk by chunk
    for chunk in iter(lambda:gz.read(chunk_size), ''):
        chunk_size = len(chunk)
        total_chunk += chunk_size
        # Timer 1
        t1_last = t1_next
        t1_next = perf_counter()
        gap = t1_next - t1_last
        t1 = t1_next
        last = last + gap
        # Accumulate time
        _, _, last_s = timerHMS(last)
        per = round(total_chunk / adjusted_estimate * 100)
        # Subpress the percentage to 100%
        per = 100 if per > 100 else per
        num = per // round(100 / bar_width)
        num = bar_width if num > bar_width else num
        # smoother at boundary estimate (just a trick)
        # if file ended and per bar have't finished, just run the remaining for per 0.4s interval 1%
        if chunk_size == 0 and per < 100:
            sleep(0.4)
            total_chunk += percentage_estimate
        # if file ended and per bar finished, a true finish, just close the subprocess, break the loop
        elif chunk_size == 0 and per == 100:
            process.stdin.close()
            break
        # the lefting suituations pipe to stdin
        else:
            _ = process.stdin.write(chunk)
        # do not display ets. on the first 3%
        if per < 3:
            proc = "\r[%3s%%]: |%-{bar_width}s| estimating ...".format(bar_width = bar_width) % (per, '|' * num)
        elif per == 100 and (total_chunk / adjusted_estimate) > 1:
            proc = "\r[%3s%%]: |%-{bar_width}s| almost ...    ".format(bar_width = bar_width) % (per, '|' * num)
        else:
            proc = "\r[%3s%%]: |%-{bar_width}s| est. %02d:%02d:%02d ".format(bar_width = bar_width) % (per, '|' * num, hour, minute, second)
        print(proc, end='', flush=True)
        # Timer 2
        t2 = perf_counter()
        # Calcu time consumed, est time left.
        t = t + (t2 - t1)
        per_iter = t / total_chunk
        # if acuumulate time > 0.5s, refresh the est.
        if last_s > 0.5:
            last = 0
            # In case strange thing happen, if i > iters, cause the image size is just an est.
            # that smaller than the actual size
            est_left = (0 if (adjusted_estimate - total_chunk) < 0 else (adjusted_estimate - total_chunk)) * per_iter
            hour, minute, second = timerHMS(est_left)
    gz.close()
    # Start a new line
    print("\r[%3s%%]: |%-{bar_width}s| loading complete".format(bar_width = bar_width) % (per, '|' * num), end = '\n', flush = True)
    # Check the subprocess is running (after stdin finish, docker load should load layers internally for a while)
    while process.poll() is None:
        try:
            for i in range(4):
                print('\rprocessing %-3s' % ('.' * i), end = '', flush = True)
                sleep(0.2)
        except subprocess.CalledProcessError as e:
            print(f"{str(e)}")
        sleep(0.1)
    else:
        # If load complete, update the base status
        exist, tags = checkImageStat(base)
    # Retag the latest image to 'latest'
    if exist:
        tags = [ int(t) for t in tags if t != 'latest']
        latest_tag = str(max(tags))
        streamProcess('docker image tag {base}:{latest_tag} {base}:latest'.format(base = base, latest_tag = latest_tag))
    # Print the total time comsumed
    hour, minute, second = timerHMS(t + perf_counter() - t2)
    print(' done.')
    print('\rtotal time consumed %02d:%02d:%02d' % (hour, minute, second))

def loadCMD(tarball):
    loadImage(tarball)

def removeImage(base, tag, force):
    '''
    '''
    import sys
    import docker
    from radiolabdocker.CheckStat import checkImageStat
    exist, tags = checkImageStat(base)
    # If not exist
    if not exist and tag not in tags:
        sys.exit('the image {base}:{tag} is not exist.'.format(base = base, tag = tag))
    print('removing the image {base}:{tag} ...'.format(base = base, tag = tag))
    client = docker.from_env()
    image = client.images.remove('{}:{}'.format(base, tag), force = force)
    print('done.')

