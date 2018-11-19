from logging import getLogger
import json

from flask import Flask, jsonify, request

from .settings import SLACK_WEBHOOK

logger = getLogger(__name__)
app = Flask(__name__)



@app.route('/qiita', methods=['POST'])
def qiita():
    """ QiitaのWebHookを受けてSlackにポストする"""
    params = json.loads(request.data)

    if params["action"] != "created":
        # created 以外だったら何もしない
        return ""

    post_to = get_target_channel(params)

    # Qiita通常投稿をパース
    if params["model"] == "item":
        user = params["user"]["url_name"]
        url = params["item"]["url"]
        title = ""
        body = params["item"]["raw_body"][:400]
        post_text = f'New: <{url}|{params["item"]["title"]}>'

    # Qiitaコメントをパース
    elif params["model"] == "comment":
        user = params["comment"]["user"]["url_name"]
        title = ""
        url = params["item"]["url"]
        body = params["comment"]["raw_body"][:400]
        post_text = 'New Comment: <{url}|{params["item"]["title"]}>'

    data = {
        "attachments": [{
            "failback": post_text,
            "pretext": post_text,
            "color": "#60c90d",
            "mrkdwn_in": ["fields"],
            "fields": [{
                "title": title,
                "value": body,
                "short": False,
            }],
        }],
        "username": "@" + user ,
        "icon_emoji": ":qiita:",
    }
    if post_to:
        data['channel'] = post_to
    logger.debug(data)

    result = requests.post(SLACK_WEBHOOK, json=data)
    return jsonify(result.json())


def get_target_channel(params):
    """ 投稿するチャンネルを決定する
    """
    # FIXME: 外部からとってくる
    for tag_data in params["item"]["tags"]:
        if tag_data["name"] == "test":
            return "test"
    return None
