import logging.config
import os

# log path
path_log = 'log'

logger_ = None


def get_logger(handler='fileAndConsole'):
    if logger_:
        return logger_
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 找到项目根目录
    project_dir = os.path.dirname(script_dir)

    # log path
    if not os.path.exists(path_log):
        os.makedirs(path_log, exist_ok=True)

    logging.config.fileConfig(f'{project_dir}/config/logging.conf')
    globals()['logger_'] = logging.getLogger(handler)
    return logger_
