import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from tg_quest.engine import StoryEngine
from tg_quest.models import Story
from tg_quest.tg.commands import CommandsHandlerBuilder
from tg_quest.tg.handlers.callback_service import CallbackService, register_callback_handler
from tg_quest.tg.handlers.node_flow_service import NodeFlowService, OrphanedMessagesCleaner
from tg_quest.tg.progress import create_progress_storage
from tg_quest.tg.renderer import Renderer

logger = logging.getLogger("tg_quest.tg.quest")


class Quest:
    def __init__(
        self,
        story: Story,
        api_token: str | None = None,
        dp: Dispatcher | None = None,
        bot: Bot | None = None,
        disable_wait: bool = False,
        progress_expired_message: str = "Your player progress has expired. Start over /start",
        already_started_text: str = "Your game already started. Have fun!",
        disable_ttl: bool = False,
        ttl_seconds: float | None = None,
        ttl_minutes: float | None = None,
        ttl_hours: float | None = None,
    ):
        self.story = story
        self._set_bot(bot, api_token)
        self._dp = dp if dp else Dispatcher(format=ParseMode)
        self._disable_wait = disable_wait
        self._disable_ttl = disable_ttl
        self._progress_expired_message = progress_expired_message
        self._already_started_text = already_started_text
        self._progress_storage = create_progress_storage(
            self.story,
            ttl_seconds=ttl_seconds,
            ttl_minutes=ttl_minutes,
            ttl_hours=ttl_hours,
        )
        self._story_engine = StoryEngine(enable_wait=not self._disable_wait)
        self._node_messenger = NodeFlowService(
            story_engine=self._story_engine,
            progress_storage=self._progress_storage,
            orphaned_messages_service=OrphanedMessagesCleaner(),
            progress_expired_message=self._progress_expired_message,
            already_started_text=self._already_started_text,
            renderer=Renderer()
        )
        self._callback_service = CallbackService(
            node_messenger=self._node_messenger
        )
        register_callback_handler(self._dp, self._callback_service)
        self._commands_handler_builder = CommandsHandlerBuilder(
            dp=self._dp,
            bot=self._bot,
            progress_storage=self._progress_storage,
            node_messenger=self._node_messenger
        )
        self._commands_handler_builder.register_start()

    def _set_bot(self, bot: Bot | None, api_token: str | None) -> None:
        if isinstance(bot, Bot):
            self._bot = bot
        elif bot is None and api_token:
            self._bot = Bot(api_token)
        else:
            raise ValueError("Neither bot nor api_token was provided")

    async def start_polling(self, *args, **kwargs) -> None:
        await self._dp.start_polling(self._bot, *args, **kwargs)
