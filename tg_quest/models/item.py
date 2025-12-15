from pydantic import BaseModel

from tg_quest.models.base import BaseGameEntity


class Item(BaseGameEntity, frozen=True):
    name: str


class UserItem(BaseGameEntity, frozen=True):
    name: str
