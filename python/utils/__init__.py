
import utils.log
from utils.log import log_traceback
from utils.exception_handler import except_output
import os


def init_logging(log_path='log.txt'):
    print('正在初始化日志服务...', end='')
    utils.log.init_log(log_path)
    print('ok')


def get_logger():
    return log.get_logger()

