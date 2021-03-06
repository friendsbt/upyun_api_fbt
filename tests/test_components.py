# coding: utf-8

import os
import shutil
import sys
import uuid
import unittest
import upyun

import upyun_api
try:
    from config import *
except ImportError:
    BUCKETNAME = os.environ['BUCKETNAME']
    UPYUN_USERNAME = os.environ['UPYUN_USERNAME']
    UPYUN_PASSWORD = os.environ['UPYUN_PASSWORD']
from MultiUpThreadPoolExecutor import MultiUpThreadPoolExecutor

curpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, curpath)

SUCCESS = "SUCCESS"
NOT_EXIST = "NOT_EXIST"
NOT_IMAGE = "NOT_IMAGE"
UPYUN_ERROR = "UPYUN_ERROR"

class TestUpyunFileAPI(unittest.TestCase):

    def setUp(self):
        self.root = "/test-%s/" % uuid.uuid4().hex
        self.up = upyun.UpYun(BUCKETNAME, UPYUN_USERNAME, UPYUN_PASSWORD, timeout=100,
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
        try:
            os.remove('test.png')
        except OSError:
            pass

    def test_get_and_put_file(self):
        result = upyun_api.upload_image('tests/test.png', self.root + 'test.png')
        self.assertEqual(result, SUCCESS)
        result = upyun_api.download_image('test.png', self.root + 'test.png')
        self.assertEqual(result, SUCCESS)
        self.assertEqual(os.path.getsize('test.png'), 13001)

    def test_non_exist(self):
        result = upyun_api.upload_image('test1.png', self.root + 'test.png')
        self.assertEqual(result, NOT_EXIST)

    def test_not_image(self):
        result = upyun_api.upload_image('.gitignore', self.root + '.gitignore')
        self.assertEqual(result, NOT_IMAGE)

        result = upyun_api.upload_image('utils.py', self.root + 'utils.py')
        self.assertEqual(result, NOT_IMAGE)


class TestUpyunFolderAPI(unittest.TestCase):

    def setUp(self):
        self.local_test_folder = 'test_folder'
        self.local_test_folder2 = 'test_folder2'
        self.upyun_test_folder = "/test_folder/"
        self.up = upyun.UpYun(BUCKETNAME, UPYUN_USERNAME, UPYUN_PASSWORD, timeout=100,
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


class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.upyun_test_folder = "/test_folder2/"
        self.temp_folder = 'temp_folder/'
        self.executor = MultiUpThreadPoolExecutor(4)
        self.up = upyun.UpYun(BUCKETNAME, UPYUN_USERNAME, UPYUN_PASSWORD, timeout=100,
                              endpoint=upyun.ED_AUTO, human=False)
        os.mkdir(self.temp_folder)

    def tearDown(self):
        try:
            self.up.delete(self.upyun_test_folder+'test.png')
        except upyun.UpYunServiceException:
            pass
        try:
            self.up.delete(self.upyun_test_folder+'test2.png')
        except upyun.UpYunServiceException:
            pass
        try:
            self.up.delete(self.upyun_test_folder)
        except upyun.UpYunServiceException:
            pass
        shutil.rmtree(self.temp_folder)


    def test_async_upload_and_download(self):
        # test upload
        f1 = self.executor.submit(
            'test_folder/test.png',
            self.upyun_test_folder+"test.png", method="PUT")
        f2 = self.executor.submit(
            'test_folder/test2.png',
            self.upyun_test_folder+"test2.png", method="PUT")
        f1.result()
        f2.result()
        shutil.copy('test_folder/test.png', self.temp_folder)
        shutil.copy('test_folder/test2.png', self.temp_folder)
        result = upyun_api.check_sync_succeed(self.temp_folder,
                                              self.upyun_test_folder)
        self.assertEqual(result, (True, ''))

        # test download
        os.remove(self.temp_folder + 'test.png')
        os.remove(self.temp_folder + 'test2.png')
        self.executor.submit(
           self.temp_folder + 'test.png',
           self.upyun_test_folder+"test.png", method="GET")
        self.executor.submit(
            self.temp_folder + 'test2.png',
            self.upyun_test_folder+"test2.png", method="GET")
        self.executor.shutdown(wait=True)
        result = upyun_api.check_sync_succeed(self.temp_folder,
                                              self.upyun_test_folder)
        self.assertEqual(result, (True, ''))