from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionPricing(Action):
    def name(self) -> Text:
        return "action_pricing"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="We have a free trial of all of Rappo AI features up to 100 users."
        )
        dispatcher.utter_message(
            text="Beyond 100 users we have flexible pricing plans."
        )
        dispatcher.utter_message(
            text="Contact our staff to know more about our pricing plans and offers."
        )
        dispatcher.utter_message(
            text="Click the button below to go back to the main menu 👇"
        )
        dispatcher.utter_message(
            json_message={
                "payload": "quickReplies",
                "data": [
                    {"payload": "/menu", "title": "⬅️ Back"},
                ],
            }
        )
        return [
            ActionExecuted("action_listen"),
            UserUttered(
                text="/menu",
                parse_data={"intent": {"name": "menu"}},
                input_channel="rest",
            ),
        ]
