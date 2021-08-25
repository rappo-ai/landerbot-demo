from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActioInstallation(Action):
    def name(self) -> Text:
        return "action_installation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="We support widgets for popular platforms like Wordpress and Shopify. Or you can just embed the generated HTML code snippet directly on your website. 🤓"
        )
        dispatcher.utter_message(
            text="Click the Live chat button to contact our team and we will be happy to help you with installation 👇"
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
