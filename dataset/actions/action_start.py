import json
import requests
from requests.structures import CaseInsensitiveDict
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.action import trigger_intent
from actions.utils.host import get_host_url
from actions.utils.json import get_json_key
from actions.utils.livechat import (
    enable_livechat,
    is_livechat_enabled,
    post_livechat_message,
)


def _is_valid_event(e):
    return (
        e.get("event") == "bot"
        and (e.get("text") or get_json_key(e, "data.custom.payload") == "quickReplies")
    ) or (e.get("event") == "user" and bool(get_json_key(e, "metadata.input_text")))


def _process_event(e):
    text = get_json_key(e, "metadata.input_text", e.get("text"))
    custom = get_json_key(e, "data.custom")

    processed_event = {
        "custom": {
            "event": e.get("event"),
            "timestamp": e.get("timestamp"),
        },
    }
    if text:
        processed_event["custom"].update({"payload": "text", "data": text})
    if custom:
        processed_event["custom"].update(custom)
    return processed_event


def _update_user_metadata(user_id, metadata):
    post_livechat_message(
        user_id,
        user_metadata=metadata,
        send_notification=False,
    )


class ActionStart(Action):
    def name(self) -> Text:
        return "action_start"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        metadata = tracker.latest_message.get("metadata", {}).get("metadata", {})
        _update_user_metadata(tracker.sender_id, metadata)

        old_events = tracker.events_after_latest_restart()
        old_events = [e for e in old_events if _is_valid_event(e)]
        old_events = [_process_event(e) for e in old_events]

        if old_events:
            headers = CaseInsensitiveDict()
            headers["Content-type"] = "application/json"
            request_data = {
                "history_events": old_events,
                "recipient_id": tracker.sender_id,
            }
            request_data_str = json.dumps(request_data)
            enqueue_history_url = get_host_url("rest", "/webhooks/rest/enqueue_history")
            requests.post(enqueue_history_url, headers=headers, data=request_data_str)

        is_livechat = is_livechat_enabled(tracker.sender_id)
        if not old_events:
            dispatcher.utter_message(
                text="Hey there, 👋 welcome to Rappo. We build tools to make chatbots 🤖, like this one!"
            )

        if not old_events or is_livechat:
            if is_livechat:
                enable_livechat(tracker.sender_id, enabled=False)
            return trigger_intent("menu", "rest")

        return []
