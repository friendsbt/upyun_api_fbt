# coding: utf-8

import os
import shutil
import sys
import uuid
import unittest
import upyun

import upyun_api
from config import *

curpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

SUCCESS = 0
IMAGE_NOT_EXIST = 1
NOT_IMAGE = 2
UPYUN_ERROR = 3

class TestUpyunFileAPI(unittest.TestCase):

    def setUp(self):
        self.root = "/test-%s/" % uuid.uuid4().hex
        self.up = upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD, timeout=100,
                              endpoint=upyun.ED_AUTO, human=False)

    def tearDown(self):
        try:
            self.up.delete(self.root + 'test.png')
        except upyun.UpYunServiceException:
            pass
        try:
            self.up.delete(self.root)
        except upyun.UpYunServiceException:
            pass
        with self.assertRaises(upyun.UpYunServiceException) as se:
            self.up.getinfo(self.root)
        self.assertEqual(se.exception.status, 404)

    def test_put_file(self):
        result = upyun_api.upload_image('tests/test.png', self.root + 'test.png')
        self.assertEqual(result, SUCCESS)

    def test_non_exist(self):
        result = upyun_api.upload_image('test1.png', self.root + 'test.png')
        self.assertEqual(result, IMAGE_NOT_EXIST)

    def test_not_image(self):
        result = upyun_api.upload_image('.gitignore', self.root + '.gitignore')
        self.assertEqual(result, NOT_IMAGE)

        result = upyun_api.upload_image('config.py', self.root + 'config.py')
        self.assertEqual(result, NOT_IMAGE)


class TestUpyunFolderAPI(unittest.TestCase):

    def setUp(self):
        self.local_test_folder = 'test_folder'
        self.local_test_folder2 = 'test_folder2'
        self.upyun_test_folder = "/test_folder/"
        self.up = upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD, timeout=100,
                              endpoint=upyun.ED_AUTO, human=False)

    def tearDown(self):
        if os.path.exists(os.path.join(curpath, self.local_test_folder2)):
            shutil.rmtree(os.path.join(curpath, self.local_test_folder2))
        pass

    def test_check_sync_succeed(self):
        result = upyun_api.check_sync_succeed(
            os.path.join(curpath, self.local_test_folder),
                                     self.upyun_test_folder)

        self.assertEqual((True, ''), result)

    def test_download_folder(self):
        upyun_api.download_folder(
            os.path.join(curpath, self.local_test_folder2),
            self.upyun_test_folder, isroot=True)

        result = upyun_api.check_sync_succeed(
            os.path.join(curpath, self.local_test_folder2),
            self.upyun_test_folder)

        self.assertEqual((True, ''), result)
