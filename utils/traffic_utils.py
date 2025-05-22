import logging
import os.path

from bilibili.event_message import EventMessage
from enums.message_type import EventType

logger = logging.getLogger('fileAndConsole')

# http setting
chunk_size = 10240


def format_file_size(size):
    size = int(size)
    # 单位列表
    units = ['B', 'KB', 'MB', 'GB']

    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    formatted_size = f"{round(size)} {units[unit_index]}"
    return formatted_size


def download_with_progress(resp, path):
    path_name = os.path.dirname(path)
    os.makedirs(path_name, exist_ok=True)
    downloaded = 0
    total_size = int(resp.headers.get('content-length', 0))
    logger.info(f'总大小: {format_file_size(total_size)}')
    with open(path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            downloaded = downloaded + len(chunk)
            percent = downloaded / total_size * 100
            if chunk:
                print(
                    f'\r{percent:.2f}%: [{"|" * int(percent // 2)}{" " * int((100 - percent) // 2)}]',
                    end="", flush=True)
                f.write(chunk)

    print(f'\r')


def download_with_progress_for_web(resp, path):
    path_name = os.path.dirname(path)
    os.makedirs(path_name, exist_ok=True)
    downloaded = 0
    total_size = int(resp.headers.get('content-length', 0))
    logger.info(f'总大小: {format_file_size(total_size)}')
    temp_percent = 0
    with open(path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            downloaded = downloaded + len(chunk)
            percent = downloaded / total_size * 100
            if chunk:
                f.write(chunk)
                integer_percent = int(percent / 1)
                if integer_percent > temp_percent:
                    temp_percent = integer_percent
                    yield EventMessage(EventType.PERCENTAGE, percent)
    yield EventMessage(EventType.OK, path)
