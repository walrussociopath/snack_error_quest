from contextvars import ContextVar
from contextlib import contextmanager
from datetime import datetime, timedelta

import asyncio
from typing import Iterator

from src.core.logger import logger


class PlayerProgress:
    """Всё про игрока и то, как он играет."""

    def __init__(self, chat_id: int, tag: str):
        self.chat_id = chat_id
        self.last_touch: datetime = datetime.now() 
        self.tag = tag
        # Все сообщения кроме последнего, которые отображаются сейчас в чате
        self.orphaned_messages_ids: list[int] = []
        self.items: list["Item"] = []
        self.selected_reactions: dict[str, list["Reaction"]] = {}
        self.current_node: str


player_progress: ContextVar[PlayerProgress] = ContextVar('player_progress')


class ProgressStorage:
    """Хранилище прогресса игроков с реализацией TTL."""

    def __init__(self, ttl_hours: int | None = None, ttl_minutes: int | None = None, ttl_seconds: int | None = None):
        self.set_ttl(ttl_hours, ttl_minutes, ttl_seconds)
        self._storage: dict[int, PlayerProgress] = {}

    def set_ttl(
        self, 
        ttl_hours: int | None = None, 
        ttl_minutes: int | None = None, 
        ttl_seconds: int | None = None
    ) -> None:
        _ttl_seconds = 0
        if ttl_hours is not None:
            _ttl_seconds += ttl_hours * 60 * 60
        if ttl_minutes is not None:
            _ttl_seconds += ttl_minutes * 60
        if ttl_seconds is not None:
            _ttl_seconds += ttl_seconds
        self._ttl_seconds = _ttl_seconds

    def create_new_player_progress(self, chat_id: int, user_tag: str) -> PlayerProgress:
        if chat_id not in self._storage:
            player_progress = PlayerProgress(chat_id=chat_id, tag=user_tag)
            self._storage[chat_id] = player_progress
        logger.info(f'Создан прогресс для игрока @{user_tag}.')
        return self._storage[chat_id]

    def get_player_progress(self, chat_id: int) -> PlayerProgress | None:
        return self._storage.get(chat_id)

    def start_cleanup_cycle(self) -> None:
        """TTL механизм."""
        asyncio.create_task(self._cleanup_cycle_coroutine())

    async def _cleanup_cycle_coroutine(self) -> None:
        while True:
            await asyncio.sleep(60)
            self._cleanup_storage()

    def _cleanup_storage(self) -> None:
        now = datetime.now()
        to_delete_chat_ids = []
        for user in self._storage.values():
            delta = now - user.last_touch 
            if delta > timedelta(seconds=self._ttl_seconds):
                to_delete_chat_ids.append(user.chat_id)

        for chat_id in to_delete_chat_ids:
            del self._storage[chat_id]
            logger.info(f'Прогресс игрока @{user.tag} удалён.')

    def is_player_progress_exists(self, chat_id: int) -> bool:
        return chat_id in self._storage


progress_storage: ProgressStorage


def init_in_memory_progress_storage():
    global progress_storage
    progress_storage = ProgressStorage(ttl_hours=24*3)
    progress_storage.start_cleanup_cycle()


class PlayerProgressNotFound(Exception):
    pass


@contextmanager
def open_player_progress(chat_id: int) -> Iterator[PlayerProgress]:
    _player_progress = progress_storage.get_player_progress(chat_id)

    if _player_progress is None:
        raise PlayerProgressNotFound
    
    token = player_progress.set(_player_progress)
    try:
        yield _player_progress
    finally:
        player_progress.reset(token)
