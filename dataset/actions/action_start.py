from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.action import trigger_intent
from actions.utils.json import get_json_key


def _is_user_or_bot_event(e):
    return e.get("event") in ["user", "bot"]


def _unpack_event(e):
    if get_json_key(e, "data.custom.event"):
        return get_json_key(e, "data.custom")
    return e


def _is_valid_event(e):
    return e.get("event") == "bot" or bool(get_json_key(e, "metadata.input_text"))


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
            _unpack_event(e)
            for e in tracker.events_after_latest_restart()
            if _is_user_or_bot_event(e)
        ]
        old_events = [e for e in old_events if _is_valid_event(e)]

        for e in old_events:
            dispatcher.utter_message(json_message=e)
        dispatcher.utter_message(
            text="Hey there, 👋 welcome to Rappo. We build tools to make chatbots 🤖, like this one!"
        )

        return trigger_intent("menu", "rest")
