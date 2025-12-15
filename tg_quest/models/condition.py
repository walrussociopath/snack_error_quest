from abc import ABC
from collections.abc import Callable
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from tg_quest.models.player.progress import Player


type Predicate = Callable[["Player"], bool]


class Condition(BaseModel):
    rule: Predicate

    next: str # Next node if rule is satisfied
    else_: str # Alternative node if rule not satisfied

    def is_satisfied(self, player: "Player") -> bool:
        """Is current player progress satisfied the condition."""
        return self.rule(player)

    @classmethod
    def all_reactions_used(cls, next: str, else_: str) -> "Condition":
        return cls(
            rule=all_reactions_used,
            next=next,
            else_=else_
        )


def all_reactions_used(player: "Player") -> bool:
    return len(player.current_node.available_reactions) == 0


class Attribute(ABC):
    pass


class _SelectedReactionCountAttr(Attribute):

    def __eq__(self, value: int) -> Predicate:
        def predicate(player: "Player") -> bool:
            return player.state.current_node.available_reactions == value

        return predicate


class _SelectedReactionsAttr(Attribute):
    @property
    def count(self) -> _SelectedReactionCountAttr:
        return _SelectedReactionCountAttr()


class Attrs:
    # Namespace for available attrs

    SelectedReactions = _SelectedReactionsAttr()
