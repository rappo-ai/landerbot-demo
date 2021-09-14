from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionLivechatMessage(Action):
    def name(self) -> Text:
        return "action_livechat_message"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("metadata")
        message_text = user_message.get("text")
        dispatcher.utter_message(
            json_message={
                "payload": "text",
                "data": message_text,
                "sender_type": "admin",
            }
        )

        return []
