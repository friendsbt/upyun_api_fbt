#!/usr/bin/python

import upyun_api
from os.path import expanduser, join
import platform
import arrow

lastsynctime = None

if True:
    now = arrow.utcnow().timestamp
    try:
        with open('lastsynctime', 'r+') as f:
            lastsynctime = f.readline().strip()
            f.seek(0, 0)
            f.write(str(now))
    except IOError:
        with open('lastsynctime', 'w') as f:
            f.write(str(now))


# upyun_api.sync_folder('C:\\Users\\dell\\Desktop\\images\\res_icon', '/static/images/res_icon')
upyun_api.sync_folder(
    '/Users/laike9m/Desktop/images', '/static/images',
    lastsynctime=int(lastsynctime)
)
# upyun_api.sync_folder('/Users/laike9m/Desktop/images/res_icon', '/static/images/res_icon')
