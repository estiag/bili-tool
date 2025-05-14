import base64
import io
import tempfile

import qrcode as qrcode

from api.api import Api
from bilibili.event_message import EventMessage
from config.logger_config import get_logger
from urllib.parse import urlunparse, urlencode, parse_qs, urlparse
import bilibili.bilibili_common as bilibili_common
import bilibili.wbi as wbi
import utils.traffic_utils as tfu
from enums.message_type import EventType
from utils import conf_util
import os
import subprocess
import utils.ffmpeg_util as ffmpeg_util
from flask import send_from_directory

logger = get_logger()


def analyze_video(bv_code_or_url):
    bv_code = bilibili_common.get_bv_code(bv_code_or_url)
    param = {}
    if bv_code.startswith('AV'):
        param.update({'aid': bv_code})
    if bv_code.startswith('BV'):
        param.update({'bvid': bv_code})
    query = urlencode(param)
    result = Api(env=bilibili_common.env_bilibili_api).path(f'/x/web-interface/wbi/view?{query}') \
        .headers(bilibili_common.get_base_headers()).send_and_get_json()
    return result


def get_cover(url):
    img_result = Api(url).headers(bilibili_common.get_base_headers()).verify(False).send()
    return img_result.get_resp()


def get_login_qrimg():
    data = Api('https://passport.bilibili.com/x/passport-login/web/qrcode/generate').headers(
        bilibili_common.get_base_headers()).send_and_get_json()

    # 创建二维码对象
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小（1 是最小版本，范围是 1 到 40）
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率
        box_size=10,  # 每个“盒子”的像素大小
        border=4,  # 边框宽度（单位为盒子数）
    )

    # 添加数据到二维码
    qr.add_data(data.get('data').get('url'))
    qr.make(fit=True)

    # 生成二维码图像
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer)  # 保存为 PNG 格式
    binary_data = buffer.getvalue()  # 获取二进制数据
    buffer.close()
    base64_str = base64.b64encode(binary_data).decode('utf-8')

    # 生成 Data URL
    mime_type = "image/png"  # 根据图像类型设置 MIME 类型
    data_url = f"data:{mime_type};base64,{base64_str}"
    return {'qrcode_key': data.get('data').get('qrcode_key'), 'img': data_url}


def get_video_info(bvid=None, avid=None, cid=None, qn=None):
    # 通过mp4接口获取分p信息
    params = {'cid': cid, 'platform': 'pc', 'fnval': '16'}
    if avid:
        params.update({'avid': avid})
    if bvid:
        params.update({'bvid': bvid})
    if qn:
        params.update({'qn': qn})
    signed_params = wbi.enc_wbi(
        params=params,
        img_key=wbi.get_wbi_keys().get('img_key'),
        sub_key=wbi.get_wbi_keys().get('sub_key'))
    query = urlencode(signed_params)
    data = ['https', 'api.bilibili.com', '/x/player/wbi/playurl', '', query, '']
    base_url = urlunparse(data)
    return Api(base_url).headers(bilibili_common.get_headers()).verify(False).send().get_resp().json()


def download_video(bvid=None, avid=None, cid=None, qn=None):
    video_info = get_video_info(bvid, avid, cid, qn)
    title = cid
    videos = video_info.get('data').get('dash').get('video')
    hit_videos = list(filter(lambda x: x.get('id') == int(qn), videos))
    if len(hit_videos) < 1:
        resp = Api(videos[0].get('backup_url')[0]).headers(bilibili_common.get_headers()).verify(False).send().get_resp()
    else:
        resp = Api(hit_videos[0].get('backup_url')[0]).headers(bilibili_common.get_headers()).verify(False).send().get_resp()
    final_video_path = f'{tempfile.gettempdir()}/{bvid}_{title}.mp4'
    tfu.download_with_progress(resp, final_video_path)
    audios = video_info.get('data').get('dash').get('audio')
    best_audio = {}
    for audio in audios:
        if not best_audio or best_audio.get('id') < audio.get('id'):
            best_audio = audio
    audio_resp = Api(best_audio.get('backup_url')[0]).headers(bilibili_common.get_headers()).verify(False).send().get_resp()
    final_audio_path = f'{tempfile.gettempdir()}/{bvid}_{title}.mp3'
    tfu.download_with_progress(audio_resp, final_audio_path)
    ffmpeg_util.combine_video(final_video_path, final_audio_path, conf_util.get_bilibili_conf("bilibili_video_path"))


def download_video_for_web(bvid=None, avid=None, cid=None, qn=None, title=None):
    yield EventMessage(EventType.STRING, '正在解析地址')
    video_info = get_video_info(bvid, avid, cid, qn)
    title = title or cid
    videos = video_info.get('data').get('dash').get('video')
    hit_videos = list(filter(lambda x: x.get('id') == int(qn), videos))
    if len(hit_videos) < 1:
        resp = Api(videos[0].get('backup_url')[0]).headers(bilibili_common.get_headers()).stream(True).verify(False).send().get_resp()
    else:
        resp = Api(hit_videos[0].get('backup_url')[0]).headers(bilibili_common.get_headers()).stream(
            True).verify(False).send().get_resp()
    final_video_path = f'{tempfile.gettempdir()}/{bvid}_{title}.mp4'
    video_save_path = None
    audio_save_path = None
    yield EventMessage(EventType.STRING, '正在下载视频')
    for chunk_event in tfu.download_with_progress_for_web(resp, final_video_path):
        if chunk_event.message_type == EventType.PERCENTAGE:
            yield chunk_event
        elif chunk_event.message_type == EventType.OK:
            video_save_path = chunk_event.message
    audios = video_info.get('data').get('dash').get('audio')
    best_audio = {}
    for audio in audios:
        if not best_audio or best_audio.get('id') < audio.get('id'):
            best_audio = audio
    yield EventMessage(EventType.STRING, '正在下载音频')
    audio_resp = Api(best_audio.get('backup_url')[0]).headers(bilibili_common.get_headers()).stream(
        True).verify(False).send().get_resp()
    final_audio_path = f'{tempfile.gettempdir()}/{bvid}_{title}.mp3'
    for chunk_event in tfu.download_with_progress_for_web(audio_resp, final_audio_path):
        if chunk_event.message_type == EventType.PERCENTAGE:
            yield chunk_event
        elif chunk_event.message_type == EventType.OK:
            audio_save_path = chunk_event.message
    yield EventMessage(EventType.STRING, f'开始合并')
    ffmpeg_util.combine_video(video_save_path, audio_save_path, conf_util.get_bilibili_conf("bilibili_video_path"))
    yield EventMessage(EventType.STRING, f'下载完成')


def login_qrcode_poll(qrcode_key):
    headers = bilibili_common.get_base_headers()
    poll_resp = Api(
        f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}') \
        .headers(headers) \
        .verify(False).send().get_resp()
    poll_json = poll_resp.json()
    vmid = ''
    if poll_json.get('data').get('code') == 0:
        logger.info('login success')
        cookie = poll_resp.headers.get('Set-Cookie') + ';buvid3=2E0558B8-BHFD-95AL-0B6D-5D43BD2CC4s1719-022052r12'
        conf_util.set_user_conf('bilibili_cookie', cookie)
        query = urlparse(poll_json.get('data').get('url')).query
        vmid = parse_qs(query).get('DedeUserID')[0]
        # 存储当前用户
        conf_util.set_user_conf('bilibili_current_vmid', vmid)
    return {
        'code': poll_json.get('data').get('code'),
        'message': poll_json.get('data').get('message'),
        'vmid': vmid
    }


def get_user_info(vmid):
    params = {'mid': vmid}
    signed_params = wbi.enc_wbi(
        params=params,
        img_key=wbi.get_wbi_keys().get('img_key'),
        sub_key=wbi.get_wbi_keys().get('sub_key'))
    query = urlencode(signed_params)
    data = ['https', 'api.bilibili.com', '/x/space/wbi/acc/info', '', query, '']
    base_url = urlunparse(data)
    api_result = Api(base_url) \
        .headers(bilibili_common.get_headers()) \
        .verify(False).send()
    return api_result.get_resp().json()


def get_user_card_info(vmid):
    params = {'mid': vmid}
    signed_params = wbi.enc_wbi(
        params=params,
        img_key=wbi.get_wbi_keys().get('img_key'),
        sub_key=wbi.get_wbi_keys().get('sub_key'))
    query = urlencode(signed_params)
    data = ['https', 'api.bilibili.com', '/x/web-interface/card', '', query, '']
    base_url = urlunparse(data)
    api_result = Api(base_url) \
        .headers(bilibili_common.get_headers()) \
        .verify(False).send()
    return api_result.get_resp().json()


def get_bilibili_video_download_files():
    video_files = []
    for filename in os.listdir(conf_util.get_bilibili_conf("bilibili_video_path")):
        file_path = os.path.join(conf_util.get_bilibili_conf("bilibili_video_path"), filename)
        if os.path.isfile(file_path) and filename.endswith(('.mp4', '.avi', '.mov')):
            video_files.append({'name': filename})
    return video_files


def get_bilibili_img_download_files():
    video_files = []
    for filename in os.listdir(conf_util.get_bilibili_conf("bilibili_image_path")):
        file_path = os.path.join(conf_util.get_bilibili_conf("bilibili_image_path"), filename)
        if os.path.isfile(file_path) and filename.endswith(('.jpg', '.png', '.nef')):
            video_files.append({'name': filename})
    return video_files


def get_bilibili_video_download_stream(filename):
    return send_from_directory(conf_util.get_bilibili_conf("bilibili_video_path"), filename)


def get_bilibili_img_download_stream(filename):
    return send_from_directory(conf_util.get_bilibili_conf("bilibili_image_path"), filename)


def get_current_vmid():
    try:
        return conf_util.get_user_conf('bilibili_current_vmid')
    except Exception as e:
        return ''
