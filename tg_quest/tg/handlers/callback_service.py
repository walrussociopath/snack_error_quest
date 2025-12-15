import logging
from collections.abc import Awaitable, Callable

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, InaccessibleMessage, MaybeInaccessibleMessage, Message

from tg_quest.models import Reaction, ReactionNotFound
from tg_quest.models.errors import InvalidCallbackMessage
from tg_quest.registry import REGISTRY
from tg_quest.tg.errors import BotMissingError, CallbackDataMissingError
from tg_quest.tg.handlers.node_flow_service import NodeFlowService

logger = logging.getLogger("tg_quest.tg.handlers.callback_handler")


def detect_reaction(callback_data: str) -> Reaction:
    if reaction := REGISTRY.reactions.get(callback_data):
        return reaction
    raise ReactionNotFound(f"Reaction with callback {callback_data} not found in REGISTRY")


class CallbackService:
    def __init__(self, node_messenger: NodeFlowService):
        self._node_messenger = node_messenger

    async def handle(self, event: CallbackQuery) -> None:
        message, bot, callback_data = self._unpack_event(event)
        reaction = detect_reaction(callback_data)
        await self._node_messenger.handle_reaction(
            reaction=reaction,
            message=message,
            bot=bot
        )

    def _unpack_event(self, event: CallbackQuery) -> tuple[Message, Bot, str]:
        self._validate_message(event.message)
        if event.data is None:
            raise CallbackDataMissingError
        if event.message.bot is None: # type: ignore
            raise BotMissingError
        return event.message, event.message.bot, event.data # type: ignore

    def _validate_message(self, message: MaybeInaccessibleMessage | None) -> None:
        if isinstance(message, Message):
            return
        elif isinstance(message, InaccessibleMessage):
            raise InvalidCallbackMessage("InaccessibleMessage в CallbackQueryHandler.message.")
        raise InvalidCallbackMessage("Нет информации о сообщении в CallbackQueryHandler.message.")


def make_callback_handler(service: CallbackService) -> Callable[[CallbackQuery], Awaitable[None]]:
    async def handler(callback: CallbackQuery) -> None:
        await service.handle(callback)
    return handler


def register_callback_handler(dp: Dispatcher, service: CallbackService) -> None:
    dp.callback_query()(make_callback_handler(service))
