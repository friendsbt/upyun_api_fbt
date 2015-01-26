#!/usr/bin/python

import upyun_api
from os.path import expanduser, join

home = expanduser("~")
upyun_api.sync_folder(join(home, 'fbt_server_py', 'static'), 'static')