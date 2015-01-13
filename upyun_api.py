# coding: utf-8

import os
import logging
import upyun
from config import *

SUCCESS = 0
IMAGE_NOT_EXIST = 1
UPYUN_ERROR = 2

LOG_FILENAME = 'upyun-api.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,)

up = upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD, timeout=30,
                 endpoint=upyun.ED_AUTO)

def upload_image(filepath, dir_on_upyun):
    """
    :param filepath: 图片的绝对路径
    :param dir_on_upyun: 在upyun 上的存储路径, 例如/static/images/user_icon
    :return: return code
    """
    if not os.path.exists(filepath):
        return IMAGE_NOT_EXIST

    with open(filepath, 'rb') as f:
        filename = os.path.basename(filepath)
        try:
            up.put(os.path.join(dir_on_upyun, filename), f, checksum=True)
        except upyun.UpYunServiceException as se:
            error_msg = "upload failed, Except an UpYunServiceException ..."+ \
                        "HTTP Status Code: " + str(se.status) + '\n' + \
                        "Error Message:    " + se.msg + "\n"
            logging.error(error_msg)
            return UPYUN_ERROR
        except upyun.UpYunClientException as ce:
            error_msg = "upload failed Except an UpYunClientException ..." +\
                        "Error Message: " + ce.msg + "\n"
            logging.error(error_msg)
            return UPYUN_ERROR
        else:
            logging.info("upload success: %s to %s" % (filepath, dir_on_upyun))
            return SUCCESS

def sync_folder(local_folder, upyun_folder):
    """
    :param local_folder: 要同步的本地路径, 绝对路径
    :param upyun_folder: 又拍云的存储路径, 绝对路径
    :return:
    """
    pass