import io
import types

import webview
from config.logger_config import get_logger
from flask import Flask, render_template, request, send_file, make_response, send_from_directory, Response

from utils import conf_util

# logger需要再引入自定义模块之前加载，否则会先加载自定义模块中的logger
logger = get_logger('serverHandler')

import bilibili.bilibili_downloader as bili_down
import bilibili.bilibili_api_downloader as bili_api_down
import bilibili.bilibili_common as bilibili_common

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bilibili/download/cover/view")
def page_bilibili_cover():
    return render_template("bilibili/download_cover.html")


@app.route("/bilibili/download/video/view")
def page_bilibili_video():
    return render_template("bilibili/download_video.html")


@app.route("/bilibili/info/followings/view")
def page_bilibili_followings():
    return render_template("bilibili/followings.html")


@app.route("/bilibili/api/download/video/view")
def page_bilibili_video_api():
    return render_template("bilibili/download_api_video.html")


@app.route("/bilibili/info/user/view")
def page_bilibili_user_info():
    return render_template("bilibili/user_info.html")


@app.route("/bilibili/video/downloaded/view")
def page_bilibili_video_downloaded():
    return render_template("bilibili/video_downloaded.html")


@app.route("/bilibili/img/downloaded/view")
def page_bilibili_img_downloaded():
    return render_template("bilibili/img_downloaded.html")


@app.route("/bilibili/info/followings/<vmid>", methods=['POST'])
def get_bilibili_followings(vmid):
    try:
        ps = request.get_json().get('ps')
        pn = request.get_json().get('pn')
        resp = bili_down.get_followings(vmid, ps=ps, pn=pn)
        if resp.get('code') not in [200, 0]:
            return make_response(resp.get('message'), 500)
        data = resp.get('data')
        for i in data.get('list'):
            face = i.get('face')
            i.update({'face_url': f'/bilibili/info/avatar?url={face}'})
        return data
    except Exception:
        return '未登录', 500


@app.route("/bilibili/info/avatar", methods=['GET'])
def get_bilibili_avatar():
    url = request.args.get('url')
    resp = bili_down.get_avatar_data(url, small=True)
    return send_file(io.BytesIO(resp.content), mimetype=resp.headers['Content-Type'])


@app.route("/bilibili/cover", methods=['GET'])
def get_bilibili_cover():
    try:
        url_or_bvcode = request.args.get('url')
        resp = bili_down.get_cover(url_or_bvcode)
        return send_file(io.BytesIO(resp.content), mimetype=resp.headers['Content-Type'])
    except Exception:
        return '解析失败', 400


@app.route("/bilibili/cover/save", methods=['GET'])
def get_bilibili_cover_and_save():
    url_or_bvcode = request.args.get('url')
    bili_down.get_cover_and_save(url_or_bvcode)
    return 'ok'


@app.route("/bilibili/video/analyze", methods=['GET'])
def analyze_bilibili_video():
    url_or_bvcode = request.args.get('url')
    try:
        detail_json = bili_down.analyze_video(url_or_bvcode)
        if not detail_json:
            return '无效的链接或BV码', 400
        return detail_json
    except:
        return '无效的链接或BV码', 400


@app.route("/bilibili/video/download", methods=['GET'])
def download_bilibili_video():
    url_or_bvcode = request.args.get('url')
    p_codes = request.args.get('p_codes')
    quality = request.args.get('quality')
    bili_down.download_video(url_or_bvcode, p_codes=p_codes, quality=quality)
    return 'success'


@app.route("/bilibili/video/download/stream", methods=['GET'])
def download_bilibili_video_stream():
    """
    Event stream的下载方式，只接收一个pcode，使前端具有展示进度条的能力
    """
    url_or_bvcode = request.args.get('url')
    p_codes = request.args.get('p_codes')
    quality = request.args.get('quality')

    def receive_message(event_action):
        for result in event_action:
            yield f'data: {result}\n\n'
        yield 'event: finish\ndata: finish.\n\n'

    return Response(
        receive_message(bili_down.download_video_for_web(url_or_bvcode, p_codes=p_codes, quality=quality)),
        mimetype='text/event-stream'
    )


@app.route("/bilibili/video/stream", methods=['GET'])
def stream_bilibili_video():
    bvid = request.args.get('bvid')
    cid = request.args.get('cid')
    quality = request.args.get('quality')
    filename = request.args.get('filename')
    resp = bili_down.download_video_stream(bvid=bvid, cid=cid, qn=quality, filename=filename)
    return send_file(io.BytesIO(resp.content), mimetype=resp.headers['Content-Type'], as_attachment=True,
                     download_name=f'{filename}.mp4')


@app.route("/bilibili/api/video/analyze", methods=['GET'])
def analyze_bilibili_video_api():
    url_or_bvcode = request.args.get('url')
    try:
        result = bili_api_down.analyze_video(url_or_bvcode)
        if result.get('data').get('videos') > 1:
            for each_video in result.get('data').get('pages'):
                each_video_result = bili_api_down.get_video_info(bvid=bilibili_common.get_bv_code(url_or_bvcode),
                                                                 cid=each_video.get('cid'))
                each_video.update({'support_formats': each_video_result.get('data').get('support_formats')})
        else:
            video_result = bili_api_down.get_video_info(bvid=bilibili_common.get_bv_code(url_or_bvcode),
                                                        cid=result.get('data').get('cid'))
            result.get('data').update({'support_formats': video_result.get('data').get('support_formats')})
        return result
    except Exception:
        return '无效的链接或BV码', 400


@app.route("/bilibili/api/cover", methods=['GET'])
def get_bilibili_cover_api():
    url_or_bvcode = request.args.get('url')
    resp = bili_api_down.get_cover(url_or_bvcode)
    return send_file(io.BytesIO(resp.content), mimetype=resp.headers['Content-Type'])


@app.route("/bilibili/api/download/video", methods=['GET'])
def download_bilibili_video_api():
    bvid = request.args.get('bvid')
    # api方式下载cid不能为空
    cids = request.args.get('cids')
    quality = request.args.get('quality')
    for cid in cids.split(','):
        bili_api_down.download_video(bvid=bvid, cid=cid.strip(), qn=quality)
    return 'ok'


@app.route("/bilibili/api/login/view", methods=['GET'])
def bilibili_api_login_view():
    return render_template("bilibili/login.html")


@app.route("/bilibili/api/qrimg", methods=['GET'])
def bilibili_api_qrimg():
    return bili_api_down.get_login_qrimg()


@app.route("/bilibili/api/qrscan", methods=['GET'])
def bilibili_api_qrscan():
    qrcode_key = request.args.get('qrcode_key')
    return bili_api_down.login_qrcode_poll(qrcode_key)


@app.route("/bilibili/info/user/<vmid>", methods=['GET'])
def get_bilibili_user_info(vmid):
    try:
        resp = bili_api_down.get_user_info(vmid)
        if resp.get('code') not in [200, 0]:
            return make_response(resp.get('message'), 500)
        data = resp.get('data')
        data.update({'face': f'/bilibili/info/avatar?url={data.get("face")}'})
        return data
    except Exception as e:
        return '未登录', 500


@app.route("/bilibili/info/user/card/<vmid>", methods=['GET'])
def get_bilibili_user_card_info(vmid):
    try:
        resp = bili_api_down.get_user_card_info(vmid)
        if resp.get('code') not in [200, 0]:
            return make_response(resp.get('message'), 500)
        data = resp.get('data')
        return data
    except Exception:
        return '未登录', 500


@app.route("/bilibili/video/download/list", methods=['GET'])
def get_bilibili_video_download_list():
    videos = bili_api_down.get_bilibili_video_download_files()
    return videos


@app.route("/bilibili/img/download/list", methods=['GET'])
def get_bilibili_img_download_list():
    imgs = bili_api_down.get_bilibili_img_download_files()
    return imgs


@app.route("/bilibili/video/download/preview", methods=['GET'])
def get_bilibili_video_download_stream():
    filename = request.args.get('filename')
    return bili_api_down.get_bilibili_video_download_stream(filename)


@app.route("/bilibili/img/download/preview", methods=['GET'])
def get_bilibili_img_download_stream():
    filename = request.args.get('filename')
    return bili_api_down.get_bilibili_img_download_stream(filename)


@app.route("/bilibili/user/current", methods=['GET'])
def bilibili_current_user():
    try:
        return bili_api_down.get_current_vmid()
    except Exception:
        return ''


@app.route("/system/user/theme", methods=['GET'])
def get_current_theme():
    try:
        return conf_util.get_user_conf('theme')
    except Exception:
        return 'light'


@app.route("/system/user/theme/<theme>", methods=['POST'])
def set_current_theme(theme):
    try:
        if theme in ['light', 'dark']:
            conf_util.set_user_conf('theme', theme)
    except Exception:
        pass
    return 'ok'


def start_server():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)


def start_webview():
    webview.create_window('BiliTool', 'http://localhost:5000/')
    webview.start(start_server)


if __name__ == "__main__":
    # 启动webview
    start_webview()
