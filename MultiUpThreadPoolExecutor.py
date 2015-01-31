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
        self.fds = {}
        self.__submit_to = 0
        super(MultiUpThreadPoolExecutor, self).__init__(max_workers)

    def _check_submit_to(self):
        self.__submit_to += 1
        if self.__submit_to >= self._max_workers:
            self.__submit_to = 0

    def succeed_callback(self, future):
        try:
            self.fds[future.filepath_local].close()
            del self.fds[future.filepath_local]
        except KeyError as e:
            logging.error(e)
        print(future.method + " " + future.filepath_on_upyun + " succeed")
        logging.info(future.method + " " + future.filepath_on_upyun + " succeed")

    def get_working_method(self, method):

        def working_method(filepath_local, filepath_on_upyun):

            if method == 'GET':
                fd = open(filepath_local, 'wb')
                fn = self.workers[self.__submit_to].get
            elif method == 'PUT':
                fd = open(filepath_local, 'rb')
                fn = self.workers[self.__submit_to].put

            self.fds[filepath_local] = fd   # store fd for future closing
            fn(filepath_on_upyun, fd)

        return working_method


    def submit(self, filepath_local, filepath_on_upyun, method="GET"):
        """
        此方法兼顾上传和下载, 根据method决定
        :param filepath_on_upyun: upyun上文件的绝对路径
        :param fd: 本地文件的fd
        :param method: [GET|PUT]
        :return:
        """
        print("assign task to worker: %d" % self.__submit_to)
        if method == 'GET' or method == 'PUT':
            working_method = self.get_working_method(method)
        else:
            logging.error("submit needs a method: [GET|PUT]")
            raise Exception("submit method wrong, use GET or PUT")

        f = super(MultiUpThreadPoolExecutor, self)\
                .submit(working_method, filepath_local, filepath_on_upyun)
        f.method = method
        f.filepath_on_upyun = filepath_on_upyun
        f.filepath_local = filepath_local
        f.add_done_callback(self.succeed_callback)
        self._check_submit_to()
        return f