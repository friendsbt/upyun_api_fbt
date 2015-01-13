# coding: utf-8

import os
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
UPYUN_ERROR = 2

class TestUpyunAPI(unittest.TestCase):

    def setUp(self):
        self.root = "/test-%s/" % uuid.uuid4().hex
        self.up = upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD, timeout=100,
                              endpoint=upyun.ED_TELECOM, human=False)

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
        result = upyun_api.upload_image('test.png', self.root)
        self.assertEqual(result, SUCCESS)

    def test_non_exist(self):
        result = upyun_api.upload_image('test1.png', self.root)
        self.assertEqual(result, IMAGE_NOT_EXIST)
