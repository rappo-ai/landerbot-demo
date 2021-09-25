from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.json import get_json_key
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

        message_metadata = get_json_key(tracker.latest_message, "metadata", {})
        message_text = message_metadata.get("input_text") or message_metadata.get(
            "text"
        )
        user_id = tracker.sender_id
        post_livechat_message(
            user_id,
            message_text=message_text,
            send_notification=True,
            notification_type="latest_user_message",
        )

        return []
