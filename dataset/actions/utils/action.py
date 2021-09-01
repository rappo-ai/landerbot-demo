from typing import Any, List, Text

from rasa_sdk.events import ActionExecuted, SlotSet, UserUttered


def set_slot(key: Text, value: Any = None, timestamp: float = None) -> List:
    return [SlotSet(key=key, value=value, timestamp=timestamp)]


def trigger_intent(
    intent_name: Text, input_channel: Text, intent_text: Text = None
) -> List:
    if not intent_text:
        intent_text = f"/{intent_name}"
    return [
        ActionExecuted("action_listen"),
        UserUttered(
            text=intent_text,
            parse_data={"intent": {"name": intent_name}},
            input_channel=input_channel,
        ),
    ]
