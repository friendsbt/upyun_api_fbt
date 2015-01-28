#!/usr/bin/python

import upyun_api
from os.path import expanduser, join

home = expanduser("~")
# upyun_api.sync_folder(join(home, 'fbt_server_py', 'static/images'), '/static/images')
upyun_api.sync_folder('C:\\Users\\dell\\Desktop\\images\\res_icon', '/static/images/res_icon')
