import subprocess
from config.logger_config import get_logger
import os
import platform
from utils.conf_util import get_ffmpeg_conf

logger = get_logger()


def get_platform():
    return platform.system().lower()


def get_ffmpeg_exec():
    if get_platform() == 'windows':
        return get_ffmpeg_conf('ffmpeg_path')
    if get_platform() == 'linux':
        return 'ffmpeg'
    if get_platform() == 'darwin':
        return 'ffmpeg'


def combine_video(video_path, audio_path, save_path):
    mp4_filename = os.path.basename(video_path)
    os.makedirs(save_path, exist_ok=True)
    final_video_path = f'{save_path}/{mp4_filename}'
    subprocess.run([f'{get_ffmpeg_exec()}',
                    '-i',
                    video_path,
                    '-i',
                    audio_path,
                    '-c', 'copy', '-y',
                    final_video_path
                    ])
    os.remove(audio_path)
    os.remove(video_path)
    logger.info(
        f'{mp4_filename} Download success, you can find it {save_path}')
