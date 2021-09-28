from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.json import get_json_key
from actions.utils.livechat import set_livechat_visibility


class ActionLivechatVisible(Action):
    def name(self) -> Text:
        return "action_livechat_visible"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        message_metadata = get_json_key(tracker.latest_message, "metadata", {})
        set_livechat_visibility(user_id, message_metadata.get("visible", False))

        return []
