from typing import Any, Text, Dict, List

from rasa_sdk import FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.utils.validate import (
    validate_email,
    validate_name,
)


class ActionValidateContactForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_contact_form"

    def validate_contact__name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        contact_name = validate_name(slot_value)
        if contact_name:
            return {"contact__name": contact_name}
        else:
            dispatcher.utter_message(
                text="Name cannot contain special characters other than apostrophe or period."
            )
            return {"contact__name": None}

    def validate_contact__email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        email_id = validate_email(slot_value)
        if email_id:
            return {"contact__email": email_id}
        else:
            dispatcher.utter_message(text="The email id is not in a valid format.")
            return {"contact__email": None}
