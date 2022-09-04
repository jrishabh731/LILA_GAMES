import logging as log
from logging import FileHandler

import os

log_level = os.getenv("LOG_LEVEL", "INFO")
log_dir = os.getenv("LOG_PATH", "")


def set_logger(path="api_service.log"):
    logger = log.getLogger("API_LOG")
    logger.setLevel(log_level)
    full_path = os.path.join(log_dir, path)
    # os.makedirs(log_dir, exist_ok=True)
    if not logger.handlers:
        handler = FileHandler(full_path)
        logFormatter = log.Formatter(
            '%(asctime)s '':%(levelname)s :%(filename)s[%(funcName)s]: %(lineno)d: %(message)s')
        handler.setFormatter(logFormatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)


set_logger()
