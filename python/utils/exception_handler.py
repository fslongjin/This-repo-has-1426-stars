from datetime import datetime
import traceback, sys
from functools import wraps


def except_output(logger):
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @wraps(func)
        def exception_print(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exc_type, exc_value, exc_traceback_obj = sys.exc_info()
                logger.error("An error occurred：{}".format(e.args) + "\nexc_type: %s" % exc_type
                             + "\nexc_value: {}".format(exc_value) + "\nexc_traceback_obj: %s" % exc_traceback_obj
                             + '\nTrace Back: %s' % traceback.extract_tb(exc_traceback_obj))
        return exception_print
    return except_execute
