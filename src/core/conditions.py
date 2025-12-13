from dataclasses import dataclass
from typing import Callable, Protocol

from core.player_progress import PlayerProgress


@dataclass
class Condition:
    # Нода, на которую осуществляется переход при срабатывании условия
    next: str
    rule: Callable[[PlayerProgress], bool]


class Predicate(Protocol):
    def __call__(self, player_progress: PlayerProgress) -> bool: ...


class Attribute:
    pass


class SelectedReactionsAttr(Attribute):
    def __eq__(self, value: int) -> Callable[[PlayerProgress], bool]:
        def callable(player_progress: PlayerProgress) -> bool:
            p = player_progress
            return len(p.selected_reactions[p.current_node]) == value
        return callable


class Attrs:
    SelectedReactions = SelectedReactionsAttr() # Количество уже выбранных реакций на ноде
