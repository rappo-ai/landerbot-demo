import logging
import os
from ruamel import yaml
from typing import Dict, Optional, Text

logger = logging.getLogger(__name__)


def get_host_url(channel, path: Optional[Text] = ""):
    with open("credentials.yml", "r") as stream:
        try:
            credentials: Dict = yaml.safe_load(stream)
            if channel == "telegram":
                telegram_credentials: Dict = credentials.get(
                    "connectors.telegram.TelegramInput", {}
                )
                return telegram_credentials.get("host_url", "") + path
            elif channel == "rest":
                return "http://rasa-client:5005" + path
        except Exception as exc:
            logger.error(exc)


def get_livechat_admin_url(path: Optional[Text] = ""):
    return os.environ["LIVECHAT_ADMIN_BASE_URL"] + path
