from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.action import set_slot, trigger_intent
from actions.utils.command import extract_command
from actions.utils.json import get_json_key


class ActionSubscribe(Action):
    def name(self) -> Text:
        return "action_subscribe"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_metadata = get_json_key(tracker.latest_message, "metadata", {})
        email = message_metadata.get("email")

        if not email:
            dispatcher.utter_message(text="Email is missing in /subscribe.")
            return []

        return set_slot(
            key="contact__email", value=email
        ) + trigger_intent("contact", "rest")
