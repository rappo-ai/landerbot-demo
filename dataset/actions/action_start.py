import json
import requests
from requests.structures import CaseInsensitiveDict
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.action import trigger_intent
from actions.utils.host import get_host_url
from actions.utils.json import get_json_key


def _is_user_or_bot_event(e):
    return e.get("event") in ["user", "bot"]


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


class ActionStart(Action):
    def name(self) -> Text:
        return "action_start"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        old_events = [
            e
            for e in tracker.events_after_latest_restart()
            if (_is_user_or_bot_event(e) and _is_valid_event(e))
        ]
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

            return []
        else:
            dispatcher.utter_message(
                text="Hey there, 👋 welcome to Rappo. We build tools to make chatbots 🤖, like this one!"
            )
            return trigger_intent("menu", "rest")
