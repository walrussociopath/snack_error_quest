
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from tg_quest.models.base import ContentType
from tg_quest.tg.handlers.node_flow_service import NodeFlowService
from tg_quest.tg.progress import InMemoryProgressStorage


class CommandsHandlerBuilder:
    def __init__(
        self,
        dp: Dispatcher,
        bot: Bot,
        progress_storage: InMemoryProgressStorage,
        node_messenger: NodeFlowService
    ):
        self.dp = dp
        self.progress_storage = progress_storage
        self._node_messenger = node_messenger
        self._bot = bot

    def register_start(
        self
    ) -> None:
        """Create start command handler."""
        async def handler(message: Message) -> None:
            chat_id = message.chat.id
            if chat_id in self.progress_storage:
                await self._node_messenger.send_already_started_message(
                    chat_id=chat_id,
                    player=self.progress_storage[chat_id],
                    bot=self._bot
                )

            player = self.progress_storage.create_player_from_message(message)
            await self._node_messenger.move_to_node(
                bot=self._bot,
                message=message,
                node=player.player.story.start_node
            )
        self.dp.message(Command("start"))(handler)


