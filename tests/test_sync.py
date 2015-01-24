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

SUCCESS = 0
IMAGE_NOT_EXIST = 1
NOT_IMAGE = 2
UPYUN_ERROR = 3

class TestSyncFolder(unittest.TestCase):
    def test_sync_folder(self):
        upyun_api.sync_folder('test_folder', '/sync/')
        result = upyun_api.check_sync_succeed('test_folder', '/sync/')
        self.assertEqual((True, ''), result)
