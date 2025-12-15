


from collections.abc import Sequence

from tg_quest.models.base import BaseGameEntity
from tg_quest.models.node import Node


class Story(BaseGameEntity, frozen=True):
    start_node: Node

    nodes: Sequence[Node]
