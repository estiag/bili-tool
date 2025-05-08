import time
import urllib.parse

import bilibili.bilibili_downloader as bili_down
import bilibili.bilibili_api_downloader as bili_api_down
import unittest

from utils import conf_util
from utils.json_util import format_json
import utils.validate_util as validate_util
from utils.ffmpeg_util import check_ffmpeg
import bilibili.bilibili_common as bilibili_common
import bilibili.wbi as wbi
from api.api import Api


class TestBilibili(unittest.TestCase):
    # url的bv号后面要加/ 否则解析不到高清视频
    def test_init_ffmpeg(self):
        check_ffmpeg()

    def test_reorganize_url(self):
        print(validate_util.is_valid_url('BV1ASD233'))
        print(bilibili_common.format_url(
            'https://www.bilibili.com/video/BV1ZSr7YoEpD/?t=6&vd_source=b32aaf28bfc421f43903e795762fa7ef', p=9))
        print(bilibili_common.format_url('BV4f', p=89))
        print(bilibili_common.format_url('https://www.bilibili.com/video/BV1XH4y1T7WC/'))

    def test_get_detail(self):
        result = bili_down.get_detail_json('BV1XH4y1T7WC')
        print(format_json(result))

    def test_download_cover(self):
        bili_down.get_cover_and_save('BV1XH4y1T7WC')

    def test_get_followings(self):
        result = bili_down.get_followings(1677924)
        print(format_json(result.get('data').get('list')))

    def test_get_video(self):
        bili_down.download_video('BV1XH4y1T7WC', quality=116)

    def test_get_video_list(self):
        bili_down.download_video('BV1Nu4y1T771')

    def test_down_stream(self):
        bili_down.download_video_stream(bvid='BV1Nu4y1T771', qn=112, cid='1380723097')

    def test_get_video_detail_api(self):
        bili_down.get_video_detail('BV1Nu4y1T771')

    def test_wbi(self):
        params = {
            'foo': '114',
            'bar': '514',
        }
        signed_params = wbi.enc_wbi(
            params,
            img_key=wbi.get_wbi_keys().get('img_key'),
            sub_key=wbi.get_wbi_keys().get('sub_key'))
        query = urllib.parse.urlencode(signed_params)
        print(signed_params)
        print(query)

    # api方式
    def test_get_detail_api(self):
        # 单个视频
        result = bili_api_down.analyze_video('BV1XH4y1T7WC')
        print(format_json(result))
        # 合集
        result = bili_api_down.analyze_video('BV1Nu4y1T771')
        print(format_json(result))

    def test_get_video_info_api(self):
        result = bili_api_down.get_video_info(bvid='BV1XH4y1T7WC', cid='1498500265')
        print(format_json(result))

    def test_download_video_api(self):
        result = bili_api_down.download_video(bvid='BV1XH4y1T7WC', cid='1498500265')
        print(format_json(result))

    def test_set_cookie_conf(self):
        conf_util.set_user_conf('bilibili_cookie', 'a')

    def test_get_video_download_list(self):
        print(bili_api_down.get_bilibili_video_download_files())

    def test_get_current_user_vmmid(self):
        print(bili_api_down.get_current_vmid())

    def test_get_theme(self):
        Api('http://localhost:5000/system/user/theme').send_and_print()

    def test_set_theme(self):
        Api('http://localhost:5000/system/user/theme/dark')\
            .method('post').send_and_print()

    def test_yield(self):
        def loop():
            for i in range(10):
                yield i
        for item in loop():
            print(item)