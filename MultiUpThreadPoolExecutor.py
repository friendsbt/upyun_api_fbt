# coding: utf-8

import os
from concurrent.futures import ThreadPoolExecutor
import upyun
try:
    from config import *
except ImportError:
    BUCKETNAME = os.environ['BUCKETNAME']
    UPYUN_USERNAME = os.environ['UPYUN_USERNAME']
    UPYUN_PASSWORD = os.environ['UPYUN_PASSWORD']
from my_logging import *


class MultiUpThreadPoolExecutor(ThreadPoolExecutor):

    def __init__(self, max_workers):
        self._max_workers = max_workers
        self.workers = [upyun.UpYun(BUCKETNAME, UPYUN_USERNAME, UPYUN_PASSWORD,
                        endpoint=upyun.ED_AUTO) for i in range(max_workers)]
        self.__submit_to = 0
        super(MultiUpThreadPoolExecutor, self).__init__(max_workers)

    def _check_submit_to(self):
        self.__submit_to += 1
        if self.__submit_to >= self._max_workers:
            self.__submit_to = 0

    @staticmethod
    def succeed_callback(future):
        print("closing fd")
        future.fd.close()
        print("fd closed: ", future.fd.closed)
        print(future.method + " " + future.filepath + " succeed")
        logging.info(future.method + " " + future.filepath + " succeed")

    def submit(self, filepath_on_upyun, fd, method="GET"):
        """
        此方法兼顾上传和下载, 根据method决定
        :param filepath_on_upyun: upyun上文件的绝对路径
        :param fd: 本地文件的fd
        :param method: [GET|PUT]
        :return:
        """
        print("assign task to worker: %d" % self.__submit_to)
        if method == 'GET':
            fn = self.workers[self.__submit_to].get
        elif method == 'PUT':
            fn = self.workers[self.__submit_to].put
        else:
            logging.error("submit needs a method: [GET|PUT]")
            raise Exception("submit method wrong, use GET or PUT")

        f = super(MultiUpThreadPoolExecutor, self)\
                .submit(fn, filepath_on_upyun, fd)
        f.fd = fd
        f.method = method
        f.filepath = filepath_on_upyun
        f.add_done_callback(self.succeed_callback)
        self._check_submit_to()
        return f