from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.livechat import post_livechat_message


class ActionLivechatReply(Action):
    def name(self) -> Text:
        return "action_livechat_reply"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("metadata")
        message_text = user_message.get("text")
        user_id = tracker.sender_id
        post_livechat_message(user_id, message_text)

        return []