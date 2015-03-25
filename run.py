#!/usr/bin/python

from os.path import expanduser, join
import platform
import threading
import arrow
import upyun_api

home = expanduser("~")

def run_sync(periodic=False):
    lastsynctime = None
    if platform.node() == 'ebs-34536':
        # on 98
        now = arrow.utcnow().timestamp
        try:
            with open('lastsynctime', 'r+') as f:
                lastsynctime = f.readline().strip()
                f.seek(0, 0)
                f.write(str(now))
        except IOError:
            with open('lastsynctime', 'w') as f:
                f.write(str(now))

    print("run sync: " + arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ'))
    upyun_api.sync_folder(
        join(home, 'latest_fbt_server_py', 'static/images'), '/static/images',
        lastsynctime=int(lastsynctime)
    )

    if periodic:
        threading.Timer(300, run_sync, (True, )).start()


if __name__ == '__main__':
    run_sync(periodic=True)
