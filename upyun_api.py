# coding: utf-8
"""
原则: 下载函数中不会进行目录拼接, 即参数中就要给出完整的目标目录
任何时候都不会上传/下载 以 '.' 开头的文件, 直接忽略掉

download_image 和 upload_image 方法只在一次性传输一张图片时使用
"""

import os
import imghdr
import shutil
from os.path import join as join_path
import upyun
from MultiUpThreadPoolExecutor import MultiUpThreadPoolExecutor
try:
    from config import *
except ImportError:
    BUCKETNAME = os.environ['BUCKETNAME']
    UPYUN_USERNAME = os.environ['UPYUN_USERNAME']
    UPYUN_PASSWORD = os.environ['UPYUN_PASSWORD']
from my_logging import *
from utils import normalize

SUCCESS = "SUCCESS"
NOT_EXIST = "NOT_EXIST"
NOT_IMAGE = "NOT_IMAGE"
UPYUN_ERROR = "UPYUN_ERROR"


up = upyun.UpYun(BUCKETNAME, UPYUN_USERNAME, UPYUN_PASSWORD, timeout=30,
                 endpoint=upyun.ED_AUTO)

def upload_image(filepath, filepath_on_upyun):
    """
    :param filepath: 图片的绝对路径
    :param dir_on_upyun: 在upyun 上的存储路径, 例如/static/images/user_icon/a.jpg
    :return: return code
    """
    filepath = os.path.realpath(filepath)
    if not os.path.exists(filepath):
        return NOT_EXIST

    if imghdr.what(filepath) is None:
        return NOT_IMAGE

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
            logging.info("upload success: %s to %s" %
                         (filepath, filepath_on_upyun))
            return SUCCESS

def download_image(filepath, filepath_on_upyun):
    """
    :param filepath: 图片的绝对路径
    :param dir_on_upyun: 在upyun 上的存储路径, 例如/static/images/user_icon/a.jpg
    :return: return code
    """
    filepath = os.path.realpath(filepath)
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'wb') as f:
        try:
            up.get(filepath_on_upyun, f)
        except upyun.UpYunServiceException as se:
            log_se(se)
            return UPYUN_ERROR
        except upyun.UpYunClientException as ce:
            log_ce(ce)
            return UPYUN_ERROR
        else:
            logging.info("download success: %s to %s" %
                         (filepath_on_upyun, filepath))
            return SUCCESS

def download_folder(local_folder, upyun_folder, file_to_download=None,
                    isroot=False):
    """ 从 upyun 下载一个文件夹到本地, 例如/upyun/images/icon -> /local/images/icon
    :param local_folder: 本地文件夹, 之前应当不存在, 否则会删掉这个文件夹
    :param upyun_folder: upyun 的路径
    :return:
    """
    if isroot:
        file_to_download = []

    if os.path.exists(local_folder):
        shutil.rmtree(local_folder, ignore_errors=True)

    os.makedirs(local_folder)

    res = up.getlist(upyun_folder)
    upyun_subdirs = {
        f.get('name'): f for f in res if f.get('type') == 'F'
                                    and not f['name'].startswith('.')
    }
    upyun_files = {
        f.get('name'): f for f in res if f.get('type') == 'N'
                                    and not f['name'].startswith('.')
    }
    for file in upyun_files.keys():
            file_to_download.append(
                (join_path(local_folder, file),
                join_path(upyun_folder, file)
            ))

    for subdir in upyun_subdirs.keys():
        download_folder(join_path(local_folder, subdir),
                        join_path(upyun_folder, subdir),
                        file_to_download=file_to_download)

    if isroot:
        with MultiUpThreadPoolExecutor(max_workers=4) as executor:
            for local_remote_tuple in file_to_download:
                fd = open(local_remote_tuple[0], 'wb')
                executor.submit(local_remote_tuple[1], fd)

        logging.info("download folder success: %s to %s" %
                     (upyun_folder, local_folder))

def check_sync_succeed(local_root_folder, upyun_root_folder):
    """ 测试用, 检查文件夹同步是否成功, 成功返回(True, ''), 失败返回(False, 'err msg')
    """
    for root, subdirs, files in os.walk(local_root_folder):
        if os.path.basename(root).startswith('.'):
            continue
        subdirs[:] = [d for d in subdirs if d[0] != '.']
        files = [f for f in files if not f.startswith('.')
                 and imghdr.what(join_path(root, f)) is not None]

        relpath = os.path.relpath(root, local_root_folder)
        upyun_folder = join_path(upyun_root_folder, relpath) \
            if relpath != '.' else upyun_root_folder

        res = up.getlist(upyun_folder)
        upyun_subdirs = {
            f.get('name'): f for f in res if f.get('type') == 'F'
                                        and not f['name'].startswith('.')
        }
        upyun_files = {
            f.get('name'): f for f in res if f.get('type') == 'N'
                                        and not f['name'].startswith('.')
        }

        if set(subdirs) != set(upyun_subdirs.keys()):
            err_msg = "local has %s in %s\n" % (str(subdirs), root)
            err_msg += "upyun has %s in %s\n" % \
                       (str(upyun_subdirs.keys()), upyun_folder)
            return False, err_msg

        if set(files) != set(upyun_files.keys()):
            err_msg = "local has %s in %s\n" % (str(files), root)
            err_msg += "upyun has %s in %s\n" % \
                       (str(upyun_files.keys()), upyun_folder)
            return False, err_msg

        for file in files:
            local_file_size = os.path.getsize(join_path(root, file))
            if local_file_size != int(upyun_files.get(file)['size']):
                err_msg = "local file %s size: %d\n" % \
                          (join_path(root, file), local_file_size)
                err_msg += "upyun file %s size: %s\n" % \
                           (join_path(upyun_folder, file),
                            upyun_files.get(file)['size'])
                return False, err_msg

    return True, ''

def sync_folder(local_root_folder, upyun_root_folder):
    """
    :param local_root_folder: 要同步的本地路径, 绝对路径
    :param upyun_root_folder: 又拍云的存储路径, 绝对路径
    这个函数的执行策略是如果有一个文件在一边没有, 那么就放到另一边, 如果都有且size 不同,
    取较新的覆盖到另一边
    :return:
    """
    local_root_folder = os.path.realpath(local_root_folder)
    if not os.path.exists(local_root_folder):
        return NOT_EXIST

    # to avoid redundant operations
    file_to_upload = []     # [(local, remote), ...]
    file_to_download = []
    folder_to_download = []

    for root, subdirs, files in os.walk(local_root_folder):
        if os.path.basename(root).startswith('.'):
            continue
        subdirs[:] = [d for d in subdirs if d[0] != '.']
        files = [f for f in files if not f.startswith('.')
                 and imghdr.what(join_path(root, f)) is not None]

        relpath = os.path.relpath(root, local_root_folder)
        upyun_folder = join_path(upyun_root_folder, relpath)
        try:
            res = up.getlist(upyun_folder)
        except upyun.UpYunServiceException as se:
            # 云端没有这个目录
            if (se.status == 404):
                for file in files:
                    file_to_upload.append(
                        (join_path(root, file),
                        normalize(join_path(upyun_folder, file)))
                    )
            else:
                log_se(se)
        except upyun.UpYunClientException as ce:
            log_ce(ce)
        else:
            # 云端有这个目录
            upyun_subdirs = {
                f.get('name'): f for f in res if f.get('type') == 'F'
                                            and not f['name'].startswith('.')
            }
            upyun_files = {
                f.get('name'): f for f in res if f.get('type') == 'N'
                                            and not f['name'].startswith('.')
            }

            # upyun has, local don't
            for f in set(upyun_files.keys()) - set(files):
                local_remote_tuple = (
                    join_path(root, f),
                    normalize(join_path(upyun_folder, f))
                )
                file_to_download.append(local_remote_tuple)

            # local has, upyun don't
            for f in set(files) - set(upyun_files.keys()):
                local_remote_tuple = (
                    join_path(root, f),
                    normalize(join_path(upyun_folder, f))
                )
                file_to_upload.append(local_remote_tuple)

            # compare files
            for f in set(files).intersection(upyun_files.keys()):
                local_file = join_path(root, f)
                if int(upyun_files[f]['size']) != os.path.getsize(local_file):
                    local_remote_tuple = (
                        local_file,
                        normalize(join_path(upyun_folder, f))
                    )
                    if os.path.getatime(local_file) > upyun_files[f]['time']:
                        file_to_upload.append(local_remote_tuple)
                    else:
                        file_to_download.append(local_remote_tuple)

            # download folder if doesn't exist
            for upyun_subdir in upyun_subdirs:
                if upyun_subdir not in subdirs:
                    folder_to_download.append(
                        (join_path(root, upyun_subdir),
                        normalize(join_path(upyun_folder, upyun_subdir)))
                    )

    with MultiUpThreadPoolExecutor(max_workers=8) as executor:
        for local_remote_tuple in file_to_download:
            # TODO: too many open files
            fd = open(local_remote_tuple[0], 'wb')
            executor.submit(local_remote_tuple[1], fd)

    with MultiUpThreadPoolExecutor(max_workers=8) as executor:
        for local_remote_tuple in file_to_upload:
            fd = open(local_remote_tuple[0], 'rb')
            executor.submit(local_remote_tuple[1], fd, method='PUT')

    for t in folder_to_download:
        download_folder(*t, isroot=True)

    return file_to_download, file_to_upload, folder_to_download