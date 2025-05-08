import json
import os
import re
import subprocess

from bs4 import BeautifulSoup
from api.api import Api
from config.logger_config import get_logger
from urllib.parse import urlunparse, urlencode
import utils.traffic_utils as tfu
import utils.ffmpeg_util as ffmpeg_util
import bilibili.bilibili_common as bilibili_common
from utils.conf_util import get_bilibili_conf
import tempfile
import bilibili.wbi as wbi

logger = get_logger()


def get_video_detail(bv_code_or_url):
    bv_code = bilibili_common.get_bv_code(bv_code_or_url)
    param = {}
    if bv_code.startswith('AV'):
        param.update({'aid': bv_code})
    if bv_code.startswith('BV'):
        param.update({'bvid': bv_code})
    query = urlencode(param)
    Api(env=bilibili_common.env_bilibili_api).path(f'/x/web-interface/wbi/view?{query}') \
        .headers(bilibili_common.get_headers()).send_and_print()


def get_detail_callback(resp, api_result):
    bv_code = bilibili_common.get_bv_code(resp.url)
    soup = BeautifulSoup(resp.text, features="html.parser")
    title = soup.find('h1', class_='video-title').text
    cover_src = soup.find('meta', attrs={'itemprop': 'image'})['content'].split('@')[0]
    # video info
    json_data = json.loads(re.findall(r'<script>window.__playinfo__=(.*?)</script>', resp.text)[0])
    # playlist info
    playlist_json_data = json.loads(
        re.findall(r'<script>window.__INITIAL_STATE__=(.*?);\(function\(\)', resp.text)[0])
    episodes = None
    sections = playlist_json_data.get('sections')
    is_list = False
    if sections:
        if len(sections) > 0:
            episodes = sections[0].get('episodes')
            is_list = True
    elif playlist_json_data.get('availableVideoList'):
        sub_video_list = bilibili_common.find_sub_video_list(playlist_json_data.get('availableVideoList'), bv_code)
        if sub_video_list:
            episodes = sub_video_list
    if episodes:
        active_episode = soup.find('div', class_='active')
        if active_episode:
            title = active_episode.find(class_='title-txt').text
            is_list = True
    # 获取视频url，如果没有获取到最佳质量则自动获取最高质量链接
    available_video = {}
    video_quality_readable = json_data.get('data').get('accept_description')
    video_quality_id = json_data.get('data').get('accept_quality')
    best_quality = str(max(video_quality_id))
    available_best_quality = '-1'
    logger.info(f'视频格式: {",".join(video_quality_readable)}')
    videos = json_data.get('data').get('dash').get('video')
    for video in videos:
        this_id = str(video.get('id'))
        find_video_by_id = available_video.get(this_id)
        if not find_video_by_id or find_video_by_id.get('bandwidth') < video.get('bandwidth'):
            available_video.update({this_id: video})
            if int(available_best_quality) < int(this_id):
                available_best_quality = this_id
    if not available_video.get(best_quality):
        logger.info('无法获取最佳视频格式，请检查cookie')
    # 获取音频url
    # choose the best quality url
    audios = json_data.get('data').get('dash').get('audio')
    best_audio = None
    for audio in audios:
        if not best_audio or best_audio.get('bandwidth') < audio.get('bandwidth'):
            best_audio = audio
    if not best_audio:
        logger.info('无法获取最佳音频格式，请检查cookie')
    video_quality_option = []
    for i in range(len(video_quality_id)):
        name_ = video_quality_readable[i]
        id_ = video_quality_id[i]
        if int(available_best_quality) < id_:
            name_ = name_ + '(需登录)'
        video_quality_option.append({'id': id_, 'name': name_})

    result = {
        'title': title,
        'cover_src': f'https:{cover_src}',
        # 'json_data': json_data,
        'episodes': episodes,
        'bv_code': bv_code,
        'is_list': is_list,
        'video_quality_readable': video_quality_readable,
        'video_quality_id': video_quality_id,
        'available_video': available_video,
        'available_best_quality': available_best_quality,
        'video_quality_option': video_quality_option,
        'best_audio': best_audio
    }
    return result


def get_avatar_data(url, small=False):
    if small:
        url = url + '@80w_80h_1c_1s.webp'
    return Api(url).headers(bilibili_common.get_headers()).send().get_resp()


def get_cover_callback(resp, api_result):
    title = bilibili_common.reorganize_title(api_result.get_callback_result().get('title'))
    bv_code = api_result.get_callback_result().get('bv_code')
    tfu.download_with_progress(resp, f'{get_bilibili_conf("bilibili_image_path")}/{bv_code}_{title}.jpg')
    logger.info(f'视频封面[{bv_code}_{title}]下载成功')


def get_cover_url(api_result):
    return api_result.get_callback_result().get('cover_src')


def get_video_url(api_result, quality):
    available_video = api_result.get_callback_result().get('available_video')
    available_best_quality = api_result.get_callback_result().get('available_best_quality')
    if not quality:
        quality = available_best_quality
    if quality not in available_video:
        logger.info(f'quality {quality} is not available, chose {available_best_quality}')
        quality = available_best_quality
    best_video = available_video.get(quality)
    logger.info(
        f'已选择质量 {quality} 分辨率:{best_video.get("width")}x{best_video.get("height")} 帧率{best_video.get("frame_rate")}')
    return best_video.get('backup_url')[0]


def save_video(resp, api_result):
    if 200 <= resp.status_code < 300:
        title = bilibili_common.reorganize_title(api_result.get_callback_result().get('title'))
        bv_code = api_result.get_callback_result().get('bv_code')
        # save file as binary
        video_path = f'{tempfile.gettempdir()}/{title}.mp4'
        tfu.download_with_progress(resp, video_path)
        logger.info(f'视频[{bv_code}_{title}]下载成功')
        return {'video_path': video_path}
    else:
        logger.error(f'下载失败, status code is {resp.status_code}')


def get_audio_url(api_result):
    best_audio = api_result.get_callback_result().get('best_audio')
    logger.info(f'已选择质量 带宽:{best_audio.get("bandwidth")}')
    return best_audio.get('backup_url')[0]


def save_audio(resp, api_result):
    if 200 <= resp.status_code < 300:
        title = bilibili_common.reorganize_title(api_result.get_callback_result().get('title'))
        bv_code = api_result.get_callback_result().get('bv_code')
        # save file as binary
        audio_path = f'{tempfile.gettempdir()}/{title}.mp3'
        tfu.download_with_progress(resp, audio_path)
        logger.info(f'音频[{bv_code}_{title}]下载成功')
        return {'audio_path': audio_path}
    else:
        logger.error(f'下载失败, status code is {resp.status_code}')


def combine_video(path_result):
    mp4_filename = path_result.get("video_path").split("/")[-1]
    final_video_path = f'{get_bilibili_conf("bilibili_video_path")}/{mp4_filename}'
    subprocess.run([f'{ffmpeg_util.ffmpeg_exe_full_path}',
                    '-i',
                    path_result.get('video_path'),
                    '-i',
                    path_result.get('audio_path'),
                    '-c', 'copy', '-y',
                    final_video_path
                    ])
    os.remove(path_result.get('audio_path'))
    os.remove(path_result.get('video_path'))
    logger.info(f'{mp4_filename} Download success, you can find it {get_bilibili_conf("bilibili_video_path")}')


def get_detail_json(url):
    """
    获取视频详细信息
    对外提供
    """
    return Api(bilibili_common.format_url(url)).headers(bilibili_common.get_headers()).callback(
        get_detail_callback).send().get_callback_result()


def get_detail(url):
    """
    获取视频详细信息
    对外提供
    """
    return Api(bilibili_common.format_url(url)).headers(bilibili_common.get_headers()).callback(
        get_detail_callback).send()


def get_cover_and_save(url):
    """
    下载指定url的视频封面
    对外提供
    """
    get_detail_api = Api(bilibili_common.format_url(url)).headers(bilibili_common.get_headers()).callback(
        get_detail_callback)
    get_detail_api.then(Api(get_cover_url).headers(bilibili_common.get_headers()).callback(get_cover_callback)).send()


def get_cover(url):
    """
    下载指定url的视频封面
    对外提供
    """
    get_detail_api_result = Api(bilibili_common.format_url(url)).headers(bilibili_common.get_headers()).callback(
        get_detail_callback).send()
    img_result = Api(get_cover_url(get_detail_api_result)).headers(bilibili_common.get_headers()).send()
    return img_result.get_resp()


def get_followings(vmid, order='desc', order_type='', pn=1, ps=20):
    """
    获取关注列表
    对外提供
    """
    api_result = Api(f'/x/relation/followings?vmid={vmid}&order={order}&order_type={order_type}&pn={pn}&ps={ps}') \
        .env(bilibili_common.env_bilibili_api) \
        .headers(bilibili_common.get_headers()) \
        .send()
    return api_result.get_resp().json()


def analyze_video(url):
    video_detail = get_detail_json(url)
    return video_detail


def download_and_combine(video_detail, quality):
    video_result = Api(get_video_url(video_detail, quality)).headers(bilibili_common.get_headers()).send()
    video_save_result = save_video(video_result.get_resp(), video_detail)
    audio_result = Api(get_audio_url(video_detail)).headers(bilibili_common.get_headers()).send()
    audio_save_result = save_audio(audio_result.get_resp(), video_detail)
    video_save_result.update(audio_save_result)
    combine_video(video_save_result)


def download_video(url, p_codes=None, quality=None):
    """
    下载指定url或bv code的视频或视频合集
    @:param p_codes 若是None, 则表示需要弹出提示手动输入p编号
    @:param quality 视频清晰度id
    对外提供
    """
    p_codes = str(p_codes)
    video_detail = get_detail(url)
    video_detail_json = video_detail.get_callback_result()
    if video_detail_json.get('is_list'):
        episodes = video_detail_json.get('episodes')
        logger.info("解析为视频合集:")
        for video in episodes:
            logger.info(f'P:{video.get("p")}, 标题:{video.get("title")}')
        if not p_codes:
            p_codes = input("请输入视频P编号下载(多个用逗号分隔,若下载全部直接回车):")
        if not p_codes or p_codes == 'all':
            episodes_for_download = episodes
        else:
            episodes_for_download = list(filter(lambda x: str(x.get('p')) in p_codes, episodes))
        for episode in episodes_for_download:
            logger.info(f'准备下载 {episode.get("title")}')
            sub_video_detail = Api(bilibili_common.format_url(url, p=episode.get('p'))).headers(
                bilibili_common.get_headers()).callback(get_detail_callback).send()
            download_and_combine(sub_video_detail, quality)
    else:
        download_and_combine(video_detail, quality)


def download_video_stream(bvid=None, avid=None, cid=None, qn=None, filename=None):
    # mp4 接口，可以直接在网页播放
    if not qn:
        qn = '116'
    params = {'cid': cid, 'platform': 'pc'}
    if avid:
        params.update({'avid': avid})
    if bvid:
        params.update({'bvid': bvid})
    if qn:
        params.update({'qn': qn})
        params.update({'fnval': '16'})
    signed_params = wbi.enc_wbi(
        params=params,
        img_key=wbi.get_wbi_keys().get('img_key'),
        sub_key=wbi.get_wbi_keys().get('sub_key'))
    query = urlencode(signed_params)
    data = ['https', 'api.bilibili.com', '/x/player/wbi/playurl', '', query, '']
    base_url = urlunparse(data)
    url_resp_json = Api(base_url).headers(bilibili_common.get_base_headers()).send().get_resp().json()
    if url_resp_json.get('data').get('dash'):
        video_url = url_resp_json.get('data').get('dash').get('video')[0].get('backup_url')[0]
    else:
        video_url = url_resp_json.get('data').get('durl')[0].get('backup_url')[0]
    video_resp = Api(video_url).headers(bilibili_common.get_headers()).send().get_resp()
    return video_resp
    # tfu.download_with_progress(video_resp, f'download/bilibili/video/{filename}')
