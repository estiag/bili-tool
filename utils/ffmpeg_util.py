from config.logger_config import get_logger
from urllib.parse import urlparse
import os
import re
import zipfile
from api.api import Api
import utils.file_util as file_util
import utils.traffic_utils as tfu
from utils.conf_util import get_ffmpeg_conf

logger = get_logger()

ffmpeg_exe_full_path = ''


def download_ffmpeg():
    def callback(resp, api_result):
        ffmpeg_path = get_ffmpeg_conf("ffmpeg_path")
        parsed_url = urlparse(get_ffmpeg_conf('ffmpeg_download_url'))
        file_name = parsed_url.path.split('/')[-1]
        if not os.path.exists(ffmpeg_path):
            os.makedirs(ffmpeg_path, exist_ok=True)
        tfu.download_with_progress(resp, f'{ffmpeg_path}/{file_name}')
        return {'message': 'ok'}

    Api(get_ffmpeg_conf('ffmpeg_download_url')).stream(True).callback(callback).send()


def extract_ffmpeg_zip(ffmpeg_zip_path):
    with zipfile.ZipFile(ffmpeg_zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'{get_ffmpeg_conf("ffmpeg_path")}')


def check_ffmpeg():
    ffmpeg_exe = None
    ffmpeg_zip = None
    # if ffmpeg is not here download it
    # if ffmpeg not extracted then extract it
    logger.info('checking ffmpeg...')
    parsed_url = urlparse(get_ffmpeg_conf('ffmpeg_download_url'))
    target_zip_name = parsed_url.path.split('/')[-1]
    # search ffmpeg.exe
    for root, dirs, files in os.walk(f'{get_ffmpeg_conf("ffmpeg_path")}'):
        if (not ffmpeg_exe or not ffmpeg_zip) and len(files) > 0:
            for each_file in files:
                if re.match(get_ffmpeg_conf('ffmpeg_exe'), each_file):
                    ffmpeg_exe = f'{root}/{each_file}'
                if re.match(f'{target_zip_name}', each_file):
                    ffmpeg_zip = f'{root}/{each_file}'

    if not ffmpeg_exe:
        if ffmpeg_zip:
            if file_util.is_zipfile(ffmpeg_zip):
                logger.info(f'ffmpeg.exe not found, but zip file is in {ffmpeg_zip}, ready to unzip')
                extract_ffmpeg_zip(ffmpeg_zip)
            else:
                logger.info(f'ffmpeg.exe not found, zip file is in {ffmpeg_zip}, but it is not zip file')
                download_ffmpeg()
                extract_ffmpeg_zip(f'{get_ffmpeg_conf("ffmpeg_path")}/{target_zip_name}')
        else:
            logger.info(f'ffmpeg.exe not found, ready to download ffmpeg')
            download_ffmpeg()
            extract_ffmpeg_zip(f'{get_ffmpeg_conf("ffmpeg_path")}/{target_zip_name}')
        for root, dirs, files in os.walk(f'{get_ffmpeg_conf("ffmpeg_path")}'):
            if len(files) > 0:
                for each_file in files:
                    if re.match(get_ffmpeg_conf('ffmpeg_exe'), each_file):
                        ffmpeg_exe = f'{root}/{each_file}'
    logger.info(f'ffmpeg is in {ffmpeg_exe}')
    global ffmpeg_exe_full_path
    ffmpeg_exe_full_path = ffmpeg_exe
