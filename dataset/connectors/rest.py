import asyncio
from datetime import datetime
import inspect
import json
import logging
from asyncio import Queue, CancelledError
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse, StreamingHTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)
import rasa.utils.endpoints

from actions.utils.date import SERVER_TZINFO
from actions.utils.json import get_json_key
from actions.utils.livechat import (
    enable_livechat,
    is_livechat_enabled,
    post_livechat_event,
    post_livechat_message,
    set_livechat_online_status,
)

logger = logging.getLogger(__name__)


def get_query_param(params, key):
    return next(iter(params[key]), "")


class QueueOutputChannel(CollectingOutputChannel):
    """Output channel that collects send messages in a list

    (doesn't send them anywhere, just collects them)."""

    @classmethod
    def name(cls) -> Text:
        return "queue"

    # noinspection PyMissingConstructor
    def __init__(self) -> None:
        super().__init__()
        self.message_queues = {}

    def latest_output(self) -> NoReturn:
        raise NotImplementedError("A queue doesn't allow to peek at messages.")

    async def _persist_message(self, message: Dict[Text, Any]) -> None:
        recipient_id = message.get("recipient_id")
        message_queue = self.get_message_queue(recipient_id)
        await message_queue.put(message)

    def get_message_queue(self, recipient_id) -> Queue:
        message_queue = self.message_queues.get(recipient_id)
        if not message_queue:
            message_queue = self.message_queues[recipient_id] = Queue()
        return message_queue


class RestInput(InputChannel):
    """A custom http input channel.

    This implementation is the basis for a custom implementation of a chat
    frontend. You can customize this to send messages to Rasa and
    retrieve responses from the assistant."""

    def __init__(
        self,
    ) -> None:
        self.queue_output_channel = QueueOutputChannel()

    @classmethod
    def name(cls) -> Text:
        return "rest"

    @staticmethod
    async def on_message_wrapper(
        on_new_message: Callable[[UserMessage], Awaitable[Any]],
        text: Text,
        queue_output_channel: QueueOutputChannel,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
        disable_nlu_bypass: bool = False,
    ) -> None:
        collector = queue_output_channel

        message = UserMessage(
            text,
            collector,
            sender_id,
            input_channel=input_channel,
            metadata=metadata,
            disable_nlu_bypass=disable_nlu_bypass,
        )
        await on_new_message(message)

    def _extract_sender(self, req: Request) -> Optional[Text]:
        return req.json.get("sender_id", None)

    # noinspection PyMethodMayBeStatic
    def _extract_message(self, req: Request) -> Optional[Text]:
        return req.json.get("text", None)

    def _extract_input_channel(self, req: Request) -> Text:
        return req.json.get("input_channel") or self.name()

    def get_metadata(self, request: Request) -> Dict[Text, Any]:
        return request.json.get("metadata", {})

    async def handle_user_message(
        self,
        should_use_stream: bool,
        on_new_message: Callable[[UserMessage], Awaitable[None]],
        sender_id: Text,
        text: Text,
        metadata: Dict[Text, Any],
        input_channel: Text,
        disable_nlu_bypass: bool,
    ) -> HTTPResponse:
        if should_use_stream:
            asyncio.ensure_future(
                self.on_message_wrapper(
                    on_new_message,
                    text,
                    self.queue_output_channel,
                    sender_id,
                    input_channel=input_channel,
                    metadata=metadata,
                    disable_nlu_bypass=disable_nlu_bypass,
                )
            )
            return response.json({"status": "ok"})
        else:
            collector = CollectingOutputChannel()
            # noinspection PyBroadException
            try:
                await on_new_message(
                    UserMessage(
                        text,
                        collector,
                        sender_id,
                        input_channel=input_channel,
                        metadata=metadata,
                        disable_nlu_bypass=disable_nlu_bypass,
                    )
                )
            except CancelledError:
                logger.error(
                    f"Message handling timed out for " f"user message '{text}'."
                )
            except Exception:
                logger.exception(
                    f"An exception occured while handling " f"user message '{text}'."
                )
            return response.json(collector.messages)

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        # noinspection PyUnusedLocal
        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            should_use_stream = rasa.utils.endpoints.bool_arg(
                request, "stream", default=False
            )
            sender_id = self._extract_sender(request)
            text = self._extract_message(request)
            input_channel = self._extract_input_channel(request)
            metadata = self.get_metadata(request)

            is_restart = text == "/restart"
            is_start = text == "/start"
            is_command = text.startswith("/")

            if is_command:
                post_livechat_event(
                    sender_id,
                    {
                        "category": "user",
                        "action": "command",
                        "label": text,
                        "metadata": metadata,
                        "ts": datetime.now(tz=SERVER_TZINFO).timestamp(),
                    },
                )

            if is_restart:
                enable_livechat(user_id=sender_id, enabled=False)
                await self.handle_user_message(
                    should_use_stream=should_use_stream,
                    on_new_message=on_new_message,
                    sender_id=sender_id,
                    text=text,
                    metadata=metadata,
                    input_channel=input_channel,
                    disable_nlu_bypass=False,
                )
            is_livechat_mode = is_livechat_enabled(user_id=sender_id)
            is_livechat_reply = is_livechat_mode and not is_command
            out_response = await self.handle_user_message(
                should_use_stream=should_use_stream,
                on_new_message=on_new_message,
                sender_id=sender_id,
                text=("/livechat_reply" if is_livechat_reply else text),
                metadata=metadata,
                input_channel=input_channel,
                disable_nlu_bypass=True,
            )

            is_notification_command = is_command and text not in ["/livechat_visible"]
            do_notification = (
                is_notification_command
                if is_livechat_mode
                else (not is_command or is_notification_command)
            )

            if do_notification:
                notification_text = metadata.get("input_text") or metadata.get("text")
                if notification_text:
                    post_livechat_message(
                        sender_id,
                        sender_type="user",
                        message_text=notification_text,
                        send_notification=is_start,
                    )

            bot_responses = json.loads(out_response.body)
            for bot_response in bot_responses:
                notification_text = ""
                notification_text = notification_text + bot_response.get("text", "")
                if (
                    not notification_text
                    and get_json_key(bot_response, "custom.payload") == "text"
                ):
                    notification_text = notification_text + get_json_key(
                        bot_response, "custom.data", ""
                    )
                if get_json_key(bot_response, "custom.payload") == "quickReplies":
                    spacer = " " if notification_text else ""
                    reply_options = [
                        r.get("title", "?")
                        for r in get_json_key(bot_response, "custom.data")
                    ]
                    options_text = ", ".join(reply_options)
                    notification_text = notification_text + spacer + f"[{options_text}]"
                send_notification = (
                    get_json_key(bot_response, "custom.payload") == "event"
                    and get_json_key(bot_response, "custom.data.name")
                    == "livechat_start"
                )
                post_livechat_message(
                    sender_id,
                    sender_type="bot",
                    message_text=notification_text,
                    send_notification=send_notification,
                )

            return out_response

        @custom_webhook.route("/events", methods=["GET"])
        async def events(request: Request) -> HTTPResponse:
            sender_id = get_query_param(request.args, "sender_id")
            if not sender_id:
                return response.json(
                    {
                        "status": "error",
                        "description": "Missing sender_id query param.",
                    }
                )

            async def streaming_fn(response: StreamingHTTPResponse) -> None:
                try:
                    set_livechat_online_status(sender_id, True)
                    while True:
                        message_queue = self.queue_output_channel.get_message_queue(
                            recipient_id=sender_id
                        )
                        message = await message_queue.get()
                        payload_json = [message]
                        payload_str = json.dumps(payload_json)
                        await response.write("data: " + payload_str + "\n\n")
                except:
                    set_livechat_online_status(sender_id, False)

            return response.stream(
                streaming_fn,
                content_type="text/event-stream",
            )

        @custom_webhook.route("/enqueue_history", methods=["POST"])
        async def enqueue(request: Request) -> HTTPResponse:
            try:
                request_dict = request.json
                recipient_id = request_dict.get("recipient_id")
                history_events = request_dict.get("history_events")
                queue = self.queue_output_channel.get_message_queue(recipient_id)
                for e in history_events:
                    await queue.put(e)
            except Exception as e:
                logger.error(f"Exception in enqueue.{e}")
            return response.json({"status": "ok"})

        @custom_webhook.route("/livechat/message", methods=["POST"])
        async def livechat_message(request: Request) -> HTTPResponse:
            if request.method == "POST":
                try:
                    request_dict = request.json
                    sender_id = self._extract_sender(request)
                    await self.handle_user_message(
                        should_use_stream=True,
                        on_new_message=on_new_message,
                        sender_id=sender_id,
                        text="/livechat_message",
                        metadata=request_dict,
                        input_channel=self.name(),
                        disable_nlu_bypass=True,
                    )
                except Exception as e:
                    logger.error(f"Exception in chat_webhook.{e}")
                    logger.debug(e, exc_info=True)

                return response.json({"status": "ok"})

        return custom_webhook
