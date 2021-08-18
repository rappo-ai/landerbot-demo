from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionMainMenu(Action):
    def name(self) -> Text:
        return "action_main_menu"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="How can I help you? Please choose one the topics listed below 👇"
        )
        dispatcher.utter_message(
            json_message={
                "payload": "quickReplies",
                "data": [
                    {"payload": "/about", "title": "❔ About Rappo"},
                    {"payload": "/pricing", "title": "💰 Pricing"},
                    {"payload": "/installation", "title": "🎚️ Installation"},
                    {"payload": "/contact", "title": "💬 Live chat"},
                ],
            }
        )

        return []
