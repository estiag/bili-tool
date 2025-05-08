import os

from utils.ffmpeg_util import check_ffmpeg
from utils.conf_util import get_bilibili_conf
check_ffmpeg()
# bilibili path
if not os.path.exists(get_bilibili_conf('bilibili_video_path')):
    os.makedirs(get_bilibili_conf('bilibili_video_path'), exist_ok=True)

if not os.path.exists(get_bilibili_conf('bilibili_image_path')):
    os.makedirs(get_bilibili_conf('bilibili_image_path'), exist_ok=True)