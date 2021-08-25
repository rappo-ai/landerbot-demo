from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.livechat import enable_livechat


class ActionOnContactFormDone(Action):
    def name(self) -> Text:
        return "action_on_contact_form_done"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        enable_livechat(tracker.sender_id, True)
        dispatcher.utter_message(
            text="Thank you for reaching out! You are now connected to one of our staff. Please type your query to begin 💬"
        )

        return []
