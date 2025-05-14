import configparser
import os

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 找到项目根目录
project_dir = os.path.dirname(script_dir)
sys_config_path = f'{project_dir}/config/system.conf'
user_config_path = f'{project_dir}/config/user.conf'
config_system = configparser.ConfigParser(interpolation=None)
config_system.read(sys_config_path, encoding='utf-8')
config_user = configparser.ConfigParser(interpolation=None)
config_user.read(user_config_path, encoding='utf-8')


# 这样也可以找到根目录
# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent))

def get_ffmpeg_conf(key):
    ffmpeg_conf = config_system.get('ffmpeg', key, raw=True)
    if key == 'ffmpeg_path':
        if ffmpeg_conf.startswith('/'):
            return ffmpeg_conf
        else:
            return f'{project_dir}/{ffmpeg_conf}'
    return ffmpeg_conf


def get_bilibili_conf(key):
    bilibili_conf = config_system.get('bilibili', key, raw=True)
    if key == 'bilibili_video_path' or key == 'bilibili_image_path':
        if os.path.isabs(bilibili_conf):
            return bilibili_conf
        else:
            return f'{project_dir}/{bilibili_conf}'
    return bilibili_conf


def set_bilibili_conf(key, value):
    config_system.set('bilibili', key, value)
    with open(f"{project_dir}/config/system.conf", 'w') as configfile:
        config_system.write(configfile)


def get_user_conf(key):
    conf_val = config_user.get('user', key, raw=True)
    return conf_val


def set_user_conf(key, value):
    config_user.set('user', key, value)
    with open(f"{project_dir}/config/user.conf", 'w') as configfile:
        config_user.write(configfile)
