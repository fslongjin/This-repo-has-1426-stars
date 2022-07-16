"""
专门用来打印日志的程序
"""

import logging
import os
from logging import handlers
import sys, traceback

log_path = ''
logger = None

class Logger(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] -%(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)





def init_log(path='log.txt'):
    global log_path, logger
    log_path = path
    logger = Logger(log_path, level='debug').logger


def get_logger():
    global logger
    return logger


def log_traceback(e):
    """
    log traceback info
    :param e: exception object
    :return: None
    """
    exc_type, exc_value, exc_traceback_obj = sys.exc_info()
    logger.error("An error occurred：{}".format(e.args) + "\nexc_type: %s" % exc_type
                 + "\nexc_value: {}".format(exc_value) + "\nexc_traceback_obj: %s" % exc_traceback_obj
                 + '\nTrace Back: %s' % traceback.extract_tb(exc_traceback_obj))
