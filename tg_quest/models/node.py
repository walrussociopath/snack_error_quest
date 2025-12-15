


from collections.abc import Sequence

from pydantic import BaseModel

from tg_quest.models.base import BaseGameEntity, ContentType
from tg_quest.models.condition import Condition
from tg_quest.models.item import Item
from tg_quest.models.reaction import Reaction


class Node(BaseGameEntity, frozen=True):

    content: ContentType

    reactions: Sequence[Reaction] = tuple()

    wait: float | None = None

    next: str | None = None

    is_terminal: bool = False

    show_items: bool = False

    can_go_back: bool = False

    add_items: Sequence[Item] | Item | None = None
