from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionResetContactForm(Action):
    def name(self) -> Text:
        return "action_reset_contact_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [
            # SlotSet("contact__name", None),
            # SlotSet("contact__email", None),
        ]