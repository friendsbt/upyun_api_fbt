#!/usr/bin/python
# coding: utf-8

import os
import upyun
import upyun_api
try:
    from config import *
except ImportError:
    UPYUN_USERNAME = os.environ['UPYUN_USERNAME']
    UPYUN_PASSWORD = os.environ['UPYUN_PASSWORD']

def run_sync(local_folder):
    up = upyun.UpYun('fbt-files', UPYUN_USERNAME, UPYUN_PASSWORD, timeout=30,
                     endpoint=upyun.ED_AUTO)
    upyun_api.sync_folder(local_folder, '/', None, up, False)


if __name__ == '__main__':
    release_folder = raw_input("输入本地release文件夹路径: ")
    if os.path.isdir(release_folder):
        run_sync(release_folder)
    else:
        print("请输入正确的本地路径")
