from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.livechat import enable_livechat, post_livechat_message


class ActionOnContactFormDone(Action):
    def name(self) -> Text:
        return "action_on_contact_form_done"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_name = tracker.get_slot("contact__name")
        user_email = tracker.get_slot("contact__email")
        enable_livechat(tracker.sender_id, user_name, user_email, True)
        post_livechat_message(
            tracker.sender_id, f"Live chat started with {user_name}, {user_email}"
        )
        dispatcher.utter_message(
            text="Thank you for reaching out! Please wait while we connect you to one of our staff. In case you don't hear from us, we will get back to you over email. Please type your query to begin 💬"
        )
        dispatcher.utter_message(
            json_message={"payload": "event", "data": {"name": "livechat_start"}}
        )
        return []
