import asyncio
from datetime import datetime, timedelta
from copy import copy

from tg_quest.models import Story, PlayerNode, Player
from tg_quest.tg.type_aliases import CHAT_ID
from aiogram.types import Message
import logging


logger = logging.getLogger('tg_quest.tg.progress')


class TGPlayer:

    player: Player
    username: str
    chat_id: int

    def __init__(self, player: Player, username: str, chat_id: int):
        self.username = username
        self.chat_id = chat_id
        self.player = player
        self.last_touch = datetime.now()
        self.active_messages_ids: list[int] = []

    @property
    def current_node(self) -> PlayerNode:
        return self.player.current_node

    @property
    def orphaned_messages_ids(self) -> list[int]:
        if len(self.active_messages_ids) > 1:
            return copy(self.active_messages_ids[:-1])
        return []

    def clear_orphaned_messages(self) -> None:
        self.active_messages_ids[:] = self.active_messages_ids[-1:] 


class InMemoryProgressStorage:
    def __init__(
        self,
        story: Story,
        ttl_hours: float | None = None,
        ttl_minutes: float | None = None,
        ttl_seconds: float | None = None
    ):
        self.story = story
        self.set_ttl_value(ttl_hours, ttl_minutes, ttl_seconds)
        self._storage: dict[CHAT_ID, TGPlayer] = {}

    def __contains__(self, chat_id: CHAT_ID) -> bool:
        return chat_id in self._storage

    def __getitem__(self, chat_id: CHAT_ID) -> TGPlayer:
        return self._storage[chat_id]

    def set_ttl_value(
        self,
        ttl_hours: float | None = None,
        ttl_minutes: float | None = None,
        ttl_seconds: float | None = None
    ) -> None:
        _ttl_seconds = 0
        if ttl_hours is not None:
            _ttl_seconds += ttl_hours * 60 * 60
        if ttl_minutes is not None:
            _ttl_seconds += ttl_minutes * 60
        if ttl_seconds is not None:
            _ttl_seconds += ttl_seconds
        self._ttl_seconds = _ttl_seconds

    def create_player_from_message(self, message: Message) -> TGPlayer:
        chat_id, username = self._unpack_message(message)
        if chat_id not in self._storage:
            player = TGPlayer(
                player=Player(self.story),
                username=username,
                chat_id=chat_id
            )
            self._storage[chat_id] = player
        logger.info("TG player @%s progress created.", username)
        return self._storage[chat_id]

    def get_player(self, chat_id: int) -> TGPlayer | None:
        return self._storage.get(chat_id)

    def start_cleanup_cycle(self) -> None:
        """Run TTL cycle."""
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
            user = self._storage[chat_id]
            del self._storage[chat_id]
            logger.debug("Player @%s progress expired and deleted.", user.username)

    def _unpack_message(self, message: Message) -> tuple[CHAT_ID, str]:
        chat_id = message.chat.id
        if message.from_user is not None and message.from_user.username is not None:
            username = message.from_user.username
        else:
            username = 'anonymous'
        return chat_id, username


def create_progress_storage(
    story: Story, 
    ttl_seconds: float | None = None,
    ttl_minutes: float | None = None,
    ttl_hours: float | None = None
) -> InMemoryProgressStorage:
    return InMemoryProgressStorage(
        story=story,
        ttl_hours=ttl_hours,
        ttl_minutes=ttl_minutes,
        ttl_seconds=ttl_seconds
    )
