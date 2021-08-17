import logging
import requests

from actions.utils.host import get_livechat_admin_url

logger = logging.getLogger(__name__)


def is_livechat_enabled(user_id):
    response_json = {}
    try:
        url = get_livechat_admin_url("/livechat/enabled")
        response = requests.get(url, params={"user_id": user_id}, timeout=5)
        response_json = response.json()
    except Exception as e:
        logger.error(e)

    return response_json.get("enabled", False)


def post_livechat_message(user_id, message_text):
    response_json = {}
    try:
        url = get_livechat_admin_url("/livechat/message")
        response = requests.post(
            url, json={"sender": user_id, "text": message_text}, timeout=5
        )
        response_json = response.json()
    except Exception as e:
        logger.error(e)

    return response_json
