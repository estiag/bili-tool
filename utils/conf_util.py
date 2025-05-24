import configparser
import os
from pathlib import Path
import shutil

# system.conf应该在用户家目录下/bilitool/conf
# 下载目录应该在用户家目录下/bilitool/download
# 先读取用户配置，如果没有在用默认配置

home_root_path = f'{Path.home()}{os.sep}bilitool'
home_conf_path = f'{home_root_path}{os.sep}config'
home_sys_config_path = f'{home_conf_path}{os.sep}system.conf'

if not os.path.exists(home_root_path):
    os.makedirs(home_root_path, exist_ok=True)
if not os.path.exists(home_conf_path):
    os.makedirs(home_conf_path, exist_ok=True)

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 找到项目根目录
project_dir = os.path.dirname(script_dir)
sys_config_path = f'{project_dir}{os.sep}config{os.sep}system.conf'
user_config_path = f'{project_dir}{os.sep}config{os.sep}user.conf'
# 这样也可以找到根目录
# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent))

init_sys_conf = False
# 如果home中system配置不存在则把默认的拷贝过去
if not os.path.exists(home_sys_config_path):
    init_sys_conf = True
    shutil.copy(sys_config_path, home_conf_path)

if not os.path.exists(user_config_path):
    with open(user_config_path, 'wb') as f:
        f.write(b'[user]\n')
        f.write(b'bilibili_cookie =\n')
        f.write(b'bilibili_current_vmid =\n')

# 配置文件准备完毕
# 读取system.conf
config_system = configparser.ConfigParser(interpolation=None)
config_system.read(home_sys_config_path, encoding='utf-8')
# 读取user.conf
config_user = configparser.ConfigParser(interpolation=None)
config_user.read(user_config_path, encoding='utf-8')


def get_ffmpeg_conf(key):
    ffmpeg_conf = config_system.get('ffmpeg', key, raw=True)
    if key == 'ffmpeg_path':
        if os.path.isabs(ffmpeg_conf):
            return ffmpeg_conf
        else:
            return f'{project_dir}{os.sep}{ffmpeg_conf}'
    return ffmpeg_conf


def get_bilibili_conf(key):
    bilibili_conf = config_system.get('bilibili', key, raw=True)
    if key == 'bilibili_video_path' or key == 'bilibili_image_path':
        if os.path.isabs(bilibili_conf):
            return bilibili_conf
        else:
            return f'{project_dir}{os.sep}{bilibili_conf}'
    return bilibili_conf


def set_bilibili_conf(key, value):
    config_system.set('bilibili', key, value)
    with open(f"{home_sys_config_path}", 'w') as configfile:
        config_system.write(configfile)


def get_user_conf(key):
    conf_val = config_user.get('user', key, raw=True)
    return conf_val


def set_user_conf(key, value):
    config_user.set('user', key, value)
    with open(f"{user_config_path}", 'w') as configfile:
        config_user.write(configfile)


# 设置绝对路径
if init_sys_conf:
    download_path = f'{Path.home()}{os.sep}Downloads{os.sep}bilitool-download'
    set_bilibili_conf('bilibili_image_path',
                      f'{download_path}{os.sep}image')
    set_bilibili_conf('bilibili_video_path',
                      f'{download_path}{os.sep}video')

# 创建下载目录
download_bilibili_img_path = get_bilibili_conf('bilibili_image_path')
download_bilibili_video_path = get_bilibili_conf('bilibili_video_path')

if not os.path.exists(download_bilibili_img_path):
    os.makedirs(download_bilibili_img_path, exist_ok=True)
if not os.path.exists(download_bilibili_video_path):
    os.makedirs(download_bilibili_video_path, exist_ok=True)
