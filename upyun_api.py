# coding: utf-8

import os
import imghdr
from os.path import join as join_path
import upyun
from config import *
from my_logging import *

SUCCESS = 0
NOT_EXIST = 1
UPYUN_ERROR = 2


up = upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD, timeout=30,
                 endpoint=upyun.ED_AUTO)

def upload_image(filepath, filepath_on_upyun):
    """
    :param filepath: 图片的绝对路径
    :param dir_on_upyun: 在upyun 上的存储路径, 例如/static/images/user_icon
    :return: return code
    """
    if not os.path.exists(filepath):
        return NOT_EXIST

    with open(filepath, 'rb') as f:
        try:
            up.put(filepath_on_upyun, f, checksum=True)
        except upyun.UpYunServiceException as se:
            log_se(se)
            return UPYUN_ERROR
        except upyun.UpYunClientException as ce:
            log_ce(ce)
            return UPYUN_ERROR
        else:
            logging.info("upload success: %s to %s" % (filepath, filepath_on_upyun))
            return SUCCESS

def download_folder(local_folder, upyun_folder):
    """ 从 upyun 下载一个文件夹到本地
    :param local_folder: 本地文件夹, 之前必须保证不存在, 否则下载失败
    :param upyun_folder: upyun 的路径
    :return:
    """
    pass

def check_sync_succeed(local_root_folder, upyun_root_folder):
    """ 测试用, 检查文件夹同步是否成功
    """
    pass

def sync_folder(local_root_folder, upyun_root_folder):
    """
    :param local_root_folder: 要同步的本地路径, 绝对路径
    :param upyun_root_folder: 又拍云的存储路径, 绝对路径
    这个函数的执行策略是如果有一个文件在一边没有, 那么就放到另一边, 如果都有且size 不同, 取
    较新的覆盖到另一边
    :return:
    """
    if not os.path.exists(local_root_folder):
        return NOT_EXIST

    # to avoid redundant operations
    file_to_upload = []     # [(local, remote), ...]
    file_to_download = []
    folder_to_download = []

    for root, subdirs, files in os.walk(local_root_folder):
        relpath = os.path.relpath(root, local_root_folder)
        upyun_folder = join_path(upyun_root_folder, relpath)
        try:
            res = up.getlist(upyun_folder)
        except upyun.UpYunServiceException as se:
            # 云端没有这个目录
            if (se.exception.status == 404):
                for file in files:
                    file_to_upload.append((join_path(root, file),
                                           join_path(upyun_folder, file)))
            else:
                log_se(se)
        except upyun.UpYunClientException as ce:
            log_ce(ce)
        else:
            # 云端有这个目录
            upyun_sudirs = {
                f.get(name): f for f in res if f.get('type') == 'F'
            }
            upyun_files = {
                f.get(name): f for f in res if f.get('type') == 'N'
            }

            # upyun has, local don't
            for f in set(upyun_files.keys()) - set(files):
                local_remote_tuple = (join_path(root, f),
                                      join_path(upyun_folder, f))
                file_to_download.append(local_remote_tuple)

            # local has, upyun don't
            for f in set(files) - set(upyun_files.keys()):
                local_remote_tuple = (join_path(root, f),
                                      join_path(upyun_folder, f))
                file_to_upload.append(local_remote_tuple)

            # compare files
            for f in set(files).intersection(upyun_files.keys()):
                local_file = join_path(root, f)
                if upyun_files[f]['size'] != os.path.getsize(local_file):
                    local_remote_tuple = (local_file, join_path(upyun_folder, f))
                    if os.path.getatime(local_file) > upyun_files[f]['time']:
                        file_to_upload.append(local_remote_tuple)
                    else:
                        file_to_download.append(local_remote_tuple)

            # download folder if doesn't exist
            for upyun_subdir in upyun_subdirs:
                if upyun_subdir not in subdirs:
                    folder_to_download.append(
                        (join_path(root, upyun_subdir),
                        join_path(upyun_folder, upyun_subdir))
                    )

    # 统一处理所有上传下载
    # TODO: