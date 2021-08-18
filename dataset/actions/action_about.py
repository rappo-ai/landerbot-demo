from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUttered
from rasa_sdk.executor import CollectingDispatcher


class ActionAbout(Action):
    def name(self) -> Text:
        return "action_about"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Rappo AI is a technology company that builds messaging automation tools, aka chatbots!"
        )
        dispatcher.utter_message(
            text="Collect user information, explain your products & services, connect live with your users, and much more through a chatbot on your website."
        )
        dispatcher.utter_message(
            text="The best part? You do not need any special app to get started! Just use the popular messaging app Telegram and contact our bot @demorappoaibot."
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
