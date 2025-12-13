import asyncio
from logging import LoggerAdapter
from typing import Any
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InaccessibleMessage
from aiogram.handlers import CallbackQueryHandler
from src.content import STORY
from src.core.dispatcher import dp
from src.core.player_progress import PlayerProgress, PlayerProgressNotFound, progress_storage, open_player_progress
from src.core.models import Node
from src.core.logger import logger
from config import config


async def start_the_game(message: Message) -> None:
    # TODO(@walrussociopath): Handler from_user = None
    player_context = progress_storage.create_new_player_progress(
        chat_id=message.chat.id,
        user_tag=message.from_user.username
    )
    player_context.orphaned_messages_ids.append(message.message_id)
    await message.answer(**STORY.start_node.message_kwargs)


@dp.message(Command('start'))
async def start_handler(message: Message) -> None:
    chat_id = message.chat.id

    if progress_storage.is_player_progress_exists(chat_id):
        await send_bot_already_started(message)
        return

    await start_the_game(message)


@dp.message(Command('help'))
async def help_handler(message: Message) -> None:
    # message.    
    await message.answer(
        text=(
            'Запутался?\n' 
            '🐞 Если что-то не работает — сюда в директ: @kolya\\_ignatev\n'
            'Вернуться к заводским настройкам (сбросить весь прогресс): /reset'
        ))


@dp.message(Command('reset'))
async def reset_handler(message: Message) -> None:
    await message.answer('Прогресс сброшен! (На самом деле нет, я ещё не доделал этот хэндлер)')


@dp.message(Command('achievements'))
async def achievements(message: Message) -> None:
    await message.answer('Тут будут твои ачивки!')


async def send_available_only_in_private_chat_message(message: Message) -> None:
    await message.answer('Сори! Бот работает только в личке!')


async def send_bot_already_started(message: Message) -> None:
    await message.answer(
        'Мы уже начали :-)\n'
        'Ткни на /reset, если хочешь сбросить весь прогресс и вернуться в стартовое меню'
    )


def link_story_to_handlers():
    for reaction in STORY.iter_reactions():
        # Регистрируем обработчик на реакцию
        logger.info(f'Хэндлер для реакции {reaction.title} index {reaction._callback_data_packed}')
        dp.callback_query(reaction.filter)(StoryReactionHandler)


class UnexpectedHandlerBehavior(Exception):
    """Что-то, чего я очень не хотел бы, чтобы произошло."""


class StoryReactionHandler(CallbackQueryHandler):
 
    def __init__(self, event: CallbackQuery, **kwargs: Any) -> None:
        super().__init__(event, **kwargs)
        self._message: Message
        self._chat_id: int
        self._set_message()

    def _set_message(self) -> None:
        if isinstance(self.message, Message):
            self._message = self.message
            self._chat_id = self.message.chat.id
            return
        elif isinstance(self.message, InaccessibleMessage):
            raise UnexpectedHandlerBehavior('InaccessibleMessage в CallbackQueryHandler.message.')
        raise UnexpectedHandlerBehavior('Нет информации о сообщении в CallbackQueryHandler.message.') 

    async def handle(self) -> None:
        logger.info(f'Обрабатывается callback из чата с @{self.from_user.username}')
        try:
            with open_player_progress(self._chat_id) as player_progress:
                self._orphaned_messages_ids = player_progress.orphaned_messages_ids
                await self._handle()
        except PlayerProgressNotFound:
            await self._handle_context_expired()

    async def _handle(self):
        current_node: Node | None = None
        current_node_message: Message

        if self.data.get('callback_data') is None:
            raise UnexpectedHandlerBehavior('callback_data не вернулась')

        await self._delete_orphaned_messages()

        while True:
            if current_node is None:
                next_node = STORY.get_next_node_by_reaction(self.data['callback_data'])
                await self._message.edit_text(**next_node.message_kwargs)
                current_node_message = self._message
            else:
                next_node = STORY.get_next_node_by_node(current_node)
                current_node_message = await self.bot.send_message(
                    chat_id=self._chat_id, **next_node.message_kwargs
                )
            
            if next_node.has_reactions():
                return
            
            self._orphaned_messages_ids.append(current_node_message.message_id)

            if config.MODE == 'PROD' and next_node.needs_a_pause():
                await asyncio.sleep(next_node.wait)
            
            current_node = next_node

    async def _delete_orphaned_messages(self) -> None:
        if self._orphaned_messages_ids:
            await self.bot.delete_messages(
                chat_id=self._message.chat.id, 
                message_ids=self._orphaned_messages_ids
            )

    async def _handle_context_expired(self) -> None:
        await self._message.answer(
            'Твой прогресс был сброшен из-за долгого отсутствия :-(\n'
            'Придётся начать сначала...'
        )
        await start_the_game(self._message)
