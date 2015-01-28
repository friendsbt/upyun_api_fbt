# coding: utf-8

import os
import shutil
import sys
import uuid
import unittest
import upyun

import upyun_api
from MultiUpThreadPoolExecutor import MultiUpThreadPoolExecutor

curpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

SUCCESS = "SUCCESS"
NOT_EXIST = "NOT_EXIST"
NOT_IMAGE = "NOT_IMAGE"
UPYUN_ERROR = "UPYUN_ERROR"

class TestSyncFolder(unittest.TestCase):
    def test_sync_folder(self):
        file_to_download, file_to_upload, folder_to_download = \
        upyun_api.sync_folder('test_folder', '/sync/')

        print(file_to_upload)
        print(file_to_upload)
        print(folder_to_download)

        result = upyun_api.check_sync_succeed('test_folder', '/sync/')
        self.assertEqual((True, ''), result)
