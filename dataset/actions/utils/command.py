import re
from typing import AnyStr, Match, Text


def extract_command(message_text: Text):
    regex = r"^(/\w+)(\s(.+))?$"

    matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
    return matches and {
        "name": matches.group(1),
        "args": matches.group(3),
    }
