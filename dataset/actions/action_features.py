from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionFeatures(Action):
    def name(self) -> Text:
        return "action_features"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="With Rappo Live Chat you can answer questions around your products & services, make recommendations, and do much more 🙌"
        )
        dispatcher.utter_message(
            text="Boost your 💰 as customers are 10x more likely to make a purchase when you reply to them instantly."
        )
        # dispatcher.utter_message(
        #    text="And the best part? You do not need any special app to get started. Our solution works entirely on the Telegram app, where your whole team can easily be a part of the customer support experience. 😮"
        # )
        dispatcher.utter_message(
            text="Click the Live chat button below to connect with us and get your chatbot today! 🥳"
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
