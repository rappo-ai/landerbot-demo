import asyncio
import inspect
import json
import logging
from asyncio import Queue, CancelledError
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse, StreamingHTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

from actions.utils.livechat import is_livechat_enabled

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
        return req.json.get("sender", None)

    # noinspection PyMethodMayBeStatic
    def _extract_message(self, req: Request) -> Optional[Text]:
        return req.json.get("message", None)

    def _extract_input_channel(self, req: Request) -> Text:
        return req.json.get("input_channel") or self.name()

    def get_metadata(self, request: Request) -> Dict[Text, Any]:
        return request.json

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
            is_livechat = is_livechat_enabled(user_id=sender_id)
            text = "/livechat_reply" if is_livechat else self._extract_message(request)
            input_channel = self._extract_input_channel(request)
            metadata = self.get_metadata(request)

            if should_use_stream:
                asyncio.ensure_future(
                    self.on_message_wrapper(
                        on_new_message,
                        text,
                        self.queue_output_channel,
                        sender_id,
                        input_channel=input_channel,
                        metadata=metadata,
                        disable_nlu_bypass=True,
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
                            disable_nlu_bypass=True,
                        )
                    )
                except CancelledError:
                    logger.error(
                        f"Message handling timed out for " f"user message '{text}'."
                    )
                except Exception:
                    logger.exception(
                        f"An exception occured while handling "
                        f"user message '{text}'."
                    )
                return response.json(collector.messages)

        @custom_webhook.route("/events")
        async def events(request: Request) -> HTTPResponse:
            sender_id = get_query_param(request.args, "sender")
            if not sender_id:
                return response.json(
                    {
                        "status": "error",
                        "description": "Missing sender_id query param.",
                    }
                )

            async def streaming_fn(response: StreamingHTTPResponse) -> None:
                while True:
                    message_queue = self.queue_output_channel.get_message_queue(
                        recipient_id=sender_id
                    )
                    message = await message_queue.get()
                    payload_json = [message]
                    payload_str = json.dumps(payload_json)
                    logger.info("PAYLOAD for SSE")
                    logger.info("data: " + payload_str + "\n\n")
                    await response.write("data: " + payload_str + "\n\n")

            return response.stream(
                streaming_fn,
                content_type="text/event-stream",
            )

        @custom_webhook.route("/livechat/message", methods=["POST"])
        async def livechat_message(request: Request) -> HTTPResponse:
            if request.method == "POST":
                try:
                    request_dict = request.json
                    sender_id = self._extract_sender(request)
                    asyncio.ensure_future(
                        self.on_message_wrapper(
                            on_new_message,
                            "/livechat_message",
                            self.queue_output_channel,
                            sender_id,
                            input_channel=self.name(),
                            metadata=request_dict,
                            disable_nlu_bypass=True,
                        )
                    )
                except Exception as e:
                    logger.error(f"Exception in chat_webhook.{e}")
                    logger.debug(e, exc_info=True)

                return response.json({"status": "ok"})

        return custom_webhook
