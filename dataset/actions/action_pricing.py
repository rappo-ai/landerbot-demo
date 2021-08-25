from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionPricing(Action):
    def name(self) -> Text:
        return "action_pricing"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="We are currently offering a free trial of all the features 🤩"
        )
        dispatcher.utter_message(
            text="Click the Live chat button to get to know more about our pricing plans and offers 👇"
        )
        dispatcher.utter_message(
            json_message={
                "payload": "quickReplies",
                "data": [
                    {"payload": "/contact", "title": "💬 Live chat"},
                    {"payload": "/menu", "title": "⬅️ Back"},
                ],
            }
        )
        return []
