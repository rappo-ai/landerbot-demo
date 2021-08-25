from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionAbout(Action):
    def name(self) -> Text:
        return "action_about"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Rappo AI is a technology company based in Bengaluru, India 🇮🇳 We build messaging automation tools."
        )
        dispatcher.utter_message(
            text="Click the Live chat button below to connect with us and know more about the team and our products. Or you could just say a hi! 🤠"
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
