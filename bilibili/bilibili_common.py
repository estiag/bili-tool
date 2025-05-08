from api.api import Env
from urllib.parse import urlparse, urlunparse
import utils.validate_util as validate_util
from utils.conf_util import get_bilibili_conf

env_bilibili = Env(host='www.bilibili.com', protocol='https')
env_bilibili_api = Env(host='api.bilibili.com', protocol='https')
env_bilibili_video = Env(host='cn-jsnt-ct-01-52.bilivideo.com', protocol='https')


def reorganize_title(title):
    """
    清除标题中的特殊字符
    """
    return title.replace('/', '').replace('&', '').replace(':', '').replace('*', 'star')


def format_url(url, p=None):
    """
    把标题格式化为可以解析的形式，包括末尾加斜线，自动补全url
    """
    reorganized_url = url
    if url.startswith('AV') or url.startswith('BV'):
        reorganized_url = f'{env_bilibili.get_env()}/video/{url}/'
    if validate_util.is_valid_url(reorganized_url):
        parsed_url = urlparse(reorganized_url)
        path = parsed_url.path
        if not parsed_url.path.endswith('/'):
            path = path + '/'
        query = parsed_url.query
        if p:
            if query:
                query = f'{query}&p={p}'
            else:
                query = f'p={p}'
        data = [parsed_url.scheme, parsed_url.hostname, path, parsed_url.port, query,
                parsed_url.fragment]
        return urlunparse(data)
    return reorganized_url


def find_sub_video_list(available_video_list, bv_code):
    """
    在数据列表中找到指定bv_code的视频列表
    """
    for item in available_video_list:
        if item.get('bvid') == bv_code:
            return item.get('list')


def get_headers():
    return {
        'origin': 'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com',
        'user-agent': get_bilibili_conf("bilibili_user_agent"),
        'cookie': get_bilibili_conf("bilibili_cookie"),
    }

def get_base_headers():
    return {
        'origin': 'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com',
        'user-agent': get_bilibili_conf("bilibili_user_agent"),
    }


def get_bv_code(url):
    try:
        if url.startswith('BV') or url.startswith('AV'):
            return url
        else:
            return urlparse(url).path.strip('/').split('/')[-1]
    except Exception:
        return ''
