import io
from config.logger_config import get_logger
from utils import conf_util

# logger需要再引入自定义模块之前加载，否则会先加载自定义模块中的logger
logger = get_logger('serverHandler')

import bilibili.bilibili_downloader as bili_down

if __name__ == "__main__":
    while True:
        url = input('请输入BV编号或视频URL\n')
        try:
            bili_down.download_video(url)
        except Exception:
            print("无法解析视频，请尝试其他编号或URL")
