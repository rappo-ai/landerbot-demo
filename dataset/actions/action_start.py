from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.action import trigger_intent


class ActionStart(Action):
    def name(self) -> Text:
        return "action_start"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        old_events = [
            e
            for e in tracker.events_after_latest_restart()
            if e.get("event") in ["user", "bot"]
        ]
        for e in old_events:
            dispatcher.utter_message(json_message=e)
        dispatcher.utter_message(
            text="Hey there, 👋 welcome to Rappo. We build tools to make chatbots 🤖, like this one!"
        )

        return trigger_intent("menu", "rest")
