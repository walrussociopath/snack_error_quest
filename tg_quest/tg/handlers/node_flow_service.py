
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot
from aiogram.types import Message

from tg_quest.engine import StoryEngine
from tg_quest.models import PlayerNode
from tg_quest.models.reaction import Reaction
from tg_quest.tg.errors import BotMissingError
from tg_quest.tg.progress import InMemoryProgressStorage, TGPlayer
from tg_quest.tg.renderer import Renderer
from tg_quest.tg.type_aliases import CHAT_ID

logger = logging.getLogger("tg_quest.tg.handlers.node_messenger")


class OrphanedMessagesCleaner:
    async def delete_orphaned_messages(self, bot: Bot, chat_id: CHAT_ID, player: TGPlayer) -> None:
        if orphaned_messages_ids := player.orphaned_messages_ids:
            await bot.delete_messages(
                chat_id=chat_id,
                message_ids=orphaned_messages_ids
            )
            player.clear_orphaned_messages()


def _inject_context(
    method: Callable
) -> Callable[..., Awaitable[bool]]: # I hate annotate async wrappers
    """Injects Telegram-related context (bot, chat_id, player) into handler methods."""

    async def wrapper(
        self: "NodeFlowService",
        *,
        message: Message,
        bot: Bot,
        **kwargs
    ) -> Any:
        message, chat_id, bot = self._unpack_contacts(message, bot)
        player = await self._get_player(bot, message, chat_id)
        if player is None:
            return None
        return await method(
            self,
            message=message,
            chat_id=chat_id,
            bot=bot,
            player=player,
            **kwargs
        )
    return wrapper


class NodeFlowService:
    """Application service responsible for presenting node transitions via Telegram interface."""

    def __init__(
        self,
        story_engine: StoryEngine,
        progress_storage: InMemoryProgressStorage,
        orphaned_messages_service: OrphanedMessagesCleaner,
        progress_expired_message: str,
        already_started_text: str,
        renderer: Renderer,
    ):
        self._story_engine = story_engine
        self._progress_storage = progress_storage
        self._progress_expired_message = progress_expired_message
        self._already_started_text = already_started_text
        self._orphaned_messages_service = orphaned_messages_service
        self._renderer = renderer

    def _extract_bot_from_message(self, message: Message) -> Bot:
        if bot := message.bot:
            return bot
        raise BotMissingError("There is no bot in message object.")

    def _unpack_contacts(self, message: Message, bot: Bot) -> tuple[Message, CHAT_ID, Bot]:
        unpacked_message = message
        unpacked_chat_id = message.chat.id
        unpacked_bot = self._extract_bot_from_message(message) if bot is None else bot
        return unpacked_message, unpacked_chat_id, unpacked_bot

    async def _get_player(self, bot: Bot, message: Message, chat_id: CHAT_ID) -> TGPlayer | None:
        if player := self._progress_storage.get_player(chat_id):
            return player
        player = self._progress_storage.create_player_from_message(message)
        await self._send_message(
            bot=bot,
            chat_id=chat_id,
            active_messages_ids=player.active_messages_ids,
            text=self._progress_expired_message
        )
        return None

    async def _move_to_node(
        self,
        *,
        node: PlayerNode,
        message: Message,
        chat_id: CHAT_ID,
        bot: Bot,
        tg_player: TGPlayer,
        reaction: Reaction | None = None
    ) -> None:
        await self._orphaned_messages_service.delete_orphaned_messages(
            bot=bot,
            chat_id=chat_id,
            player=tg_player
        )

        if tg_player.active_messages_ids:
            is_first_node = True
        else:
            is_first_node = False

        async for node in self._story_engine.walk_to_node(
            new_node=node,
            player=tg_player.player,
            reaction=reaction
        ):
            if is_first_node:
                await self._edit_message(
                    **self._renderer.render_current_node(tg_player),
                    message=message,
                    active_messages_ids=tg_player.active_messages_ids
                )
                is_first_node = False
            else:
                _ = await self._send_message(
                    bot,
                    chat_id,
                    tg_player.active_messages_ids,
                    **self._renderer.render_current_node(tg_player)
                )

    @_inject_context
    async def move_to_node(
        self,
        *,
        node: PlayerNode,
        message: Message,
        bot: Bot,
        chat_id: CHAT_ID,
        player: TGPlayer,
        reaction: Reaction | None = None
    ) -> None:
        await self._move_to_node(
            node=node,
            chat_id=chat_id,
            bot=bot,
            tg_player=player,
            message=message
        )

    @_inject_context
    async def handle_reaction(
        self,
        *,
        reaction: Reaction,
        message: Message,
        bot: Bot,
        chat_id: CHAT_ID,
        player: TGPlayer
    ) -> None:
        new_node = self._story_engine.resolve_new_node_by_reaction(reaction, player.player)
        await self._move_to_node(
            node=new_node,
            chat_id=chat_id,
            bot=bot,
            tg_player=player,
            message=message
        )

    async def send_already_started_message(
        self,
        *,
        chat_id: CHAT_ID,
        bot: Bot,
        player: TGPlayer
    ) -> None:
        await self._send_message(
            bot=bot,
            chat_id=chat_id,
            active_messages_ids=player.active_messages_ids,
            text=self._already_started_text
        )

    async def _edit_message(self, message: Message, active_messages_ids: list[int], **message_kwargs) -> None:
        await message.edit_text(
            **message_kwargs
        )

    async def _send_message(self, bot: Bot, chat_id: int, active_messages_ids: list[int], **message_kwargs) -> Message:
        message = await bot.send_message(
            chat_id=chat_id,
            **message_kwargs
        )
        active_messages_ids.append(message.message_id)
        return message
