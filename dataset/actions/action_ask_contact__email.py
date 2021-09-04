from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionAskContactEmail(Action):
    def name(self) -> Text:
        return "action_ask_contact__email"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        latest_intent_name = tracker.latest_message.get("intent", {}).get("name")
        if latest_intent_name not in ["livechat_reply", "livechat_message"]:
            dispatcher.utter_message(text="What is your email id?")

        return []
