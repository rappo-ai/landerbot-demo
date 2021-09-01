from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.action import set_slot, trigger_intent
from actions.utils.command import extract_command


class ActionSubscribe(Action):
    def name(self) -> Text:
        return "action_subscribe"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("metadata")
        message_text = user_message.get("text")

        matches = extract_command(message_text)
        if not matches:
            dispatcher.utter_message(text="The command syntax is invalid.")
            return []

        return set_slot(key="contact__email", value=matches.get("args")).extend(
            trigger_intent("contact", "rest")
        )
