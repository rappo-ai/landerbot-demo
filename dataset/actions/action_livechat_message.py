from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.json import get_json_key


class ActionLivechatMessage(Action):
    def name(self) -> Text:
        return "action_livechat_message"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_metadata = get_json_key(tracker.latest_message, "metadata", {})
        message_text = message_metadata.get("text")
        dispatcher.utter_message(
            json_message={
                "payload": "text",
                "data": message_text,
                "sender_type": "admin",
            }
        )

        return []
