

from tg_quest.models.base import BaseGameEntity
from tg_quest.models.condition import Condition


class Reaction(BaseGameEntity, frozen=True):
    title: str # Reaction display title

    next: str | Condition # Next node to move

    single_use: bool = False # After use not available on parent node anymore

    @classmethod
    def once(
        cls,
        title: str,
        next: str | Condition    
    ) -> "Reaction":
        return cls(
            title=title,
            next=next
        )

