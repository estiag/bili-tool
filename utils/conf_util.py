import configparser
import os

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 找到项目根目录
project_dir = os.path.dirname(script_dir)
config = configparser.ConfigParser(interpolation=None)
config.read(f"{project_dir}/config/system.conf", encoding='utf-8')


# 这样也可以找到根目录
# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent))

def get_ffmpeg_conf(key):
    ffmpeg_conf = config.get('ffmpeg', key, raw=True)
    if key == 'ffmpeg_path':
        if ffmpeg_conf.startswith('/'):
            return ffmpeg_conf
        else:
            return f'{project_dir}/{ffmpeg_conf}'
    return ffmpeg_conf


def get_bilibili_conf(key):
    bilibili_conf = config.get('bilibili', key, raw=True)
    if key == 'bilibili_video_path' or key == 'bilibili_image_path':
        if bilibili_conf.startswith('/'):
            return bilibili_conf
        else:
            return f'{project_dir}/{bilibili_conf}'
    return bilibili_conf


def set_bilibili_conf(key, value):
    config.set('bilibili', key, value)
    with open(f"{project_dir}/config/system.conf", 'w') as configfile:
        config.write(configfile)
