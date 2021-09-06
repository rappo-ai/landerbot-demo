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


def enable_livechat(user_id, enabled=True):
    try:
        url = get_livechat_admin_url("/livechat/enabled")
        response = requests.post(
            url,
            json={
                "user_id": user_id,
                "enabled": enabled,
            },
            timeout=5,
        )
    except Exception as e:
        logger.error(e)


def post_livechat_message(
    user_id,
    sender_type="user",
    message_text=None,
    user_metadata=None,
    send_notification=True,
):
    response_json = {}
    try:
        url = get_livechat_admin_url("/livechat/message")
        request_body = {
            "sender_id": user_id,
            "sender_type": sender_type,
            "send_notification": send_notification,
        }
        if message_text:
            request_body.update(
                {
                    "message_text": message_text,
                }
            )
        if user_metadata:
            request_body.update(
                {
                    "user_metadata": user_metadata,
                }
            )
        response = requests.post(url, json=request_body, timeout=5)
        response_json = response.json()
    except Exception as e:
        logger.error(e)

    return response_json
