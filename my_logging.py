import upyun
import logging
import os

if not os.path.exists("logs"):
    os.mkdir("logs")

LOG_FILENAME = 'logs/upyun-api.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO,)

def log_se(se):
    if not isinstance(se, upyun.UpYunServiceException):
        logging.error("logging error: ", str(se))
        raise se

    error_msg = "upload failed, Except an UpYunServiceException ..."+ \
                "HTTP Status Code: " + str(se.status) + '\n' + \
                "Error Message:    " + se.msg + "\n"
    logging.error(error_msg)

def log_ce(ce):
    if not isinstance(ce, upyun.UpYunClientException):
        logging.error("logging error: ", str(ce))
        raise ce

    error_msg = "upload failed Except an UpYunClientException ..." + \
                "Error Message: " + ce.msg + "\n"
    logging.error(error_msg)
