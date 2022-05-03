
from time import strftime


path = './build'
base = 'radiolab_docker'
saveImage(path, base)

def saveImage(path, base, tag = 'latest'):
    # modified from https://github.com/docker/docker-py/issues/1352#issuecomment-266853096
    import docker
    import gzip
    import datetime
    from time import perf_counter
    from radiolabdocker.CheckStat import checkImageStat
    def timerHMS(time):
        hour = time // 3600
        minute = (time - 3600 * hour) // 60
        second = (time - 3600 * hour - 60 * minute) // 1
        return (hour, minute, second)
    client = docker.from_env(timeout = 1800)
    tag = int(tag) if tag != 'latest' else tag
    exist, tags = checkImageStat(base)
    if exist:
        tags = [ int(t) for t in tags if t != 'latest']
        if tag == 'latest':
            tag = str(max(tags))
        elif tag in tags:
            tag = str(tag)
        else:
            raise Exception('the tag is not valid')
        image = client.images.get('{}:{}'.format(base, tag))
        image_size = image.attrs['VirtualSize']
        chunk_size = 32768
        date = datetime.datetime.now().strftime('%Y%m%d')
        tarball = '{path}/{base}#{tag}_{date}.tar.gz'.format(
            path = path,
            base = base,
            tag = tag,
            date = date)
        url = client.api._url('/images/{0}/get', image.id)
        print('getting data from {}:{} ...'.format(base, tag))
        tl1 = perf_counter()
        res = client.api._get(url, stream=True)
        chunks = res.iter_content(chunk_size)
        length = round(image_size / chunk_size)
        tl2 = perf_counter()
        tl = tl2 - tl1
        hour, minute, second = timerHMS(tl)
        print('\rconsumed %02d:%02d:%02d' % (hour, minute, second))
        print('saving {}:{} to {}'.format(base, tag, tarball))
        with gzip.open(tarball, 'wb') as tf:
            i = 1
            t = 0
            hour = 0
            minute = 0
            second = 0
            for chunk in chunks:
                t1 = perf_counter()
                per = round(i / length * 100)
                per = 100 if per > 100 else per
                num = per // 2
                subpress_output = tf.write(chunk)
                process = "\r[%3s%%]: |%-50s| est. %02d:%02d:%02d " % (per, '|' * num, hour, minute, second)
                print(process, end='', flush=True)
                t2 = perf_counter()
                t = t + (t2 - t1)
                per_iter = t / i
                est_left = (0 if (length - i) < 0 else (length - i)) * per_iter
                hour, minute, second = timerHMS(est_left)
                i += 1
            hour, minute, second = timerHMS(t + tl)
            print('\r\nDone. Total time consumed %02d:%02d:%02d' % (hour, minute, second))
            tf.close()