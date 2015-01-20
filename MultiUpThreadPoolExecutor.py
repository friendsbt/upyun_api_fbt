# coding: utf-8

from concurrent.futures import ThreadPoolExecutor
import upyun
from config import *


class MultiUpThreadPoolExecutor(ThreadPoolExecutor):

    def __init__(self, max_workers):
        self._max_workers = max_workers
        self.workers = [upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD,
                        endpoint=upyun.ED_AUTO) for i in range(max_workers)]
        self.submit_to = 0
        super(MultiUpThreadPoolExecutor, self).__init__(max_workers)

    def _check_submit_to(self):
        self.submit_to += 1
        if self.submit_to >= self._max_workers:
            self.submit_to = 0

    def submit(self, local_remote_tuple, fd):
        print("assign task to worker: %d" % self.submit_to)
        fn = self.workers[self.submit_to].get
        f = super(MultiUpThreadPoolExecutor, self).submit(fn, local_remote_tuple, fd)
        self._check_submit_to()
        return f