from tg_quest.models import Node, Reaction
from tg_quest.models.base import EntityCode


class PlayerNode:
    original_node: Node

    available_reactions: dict[EntityCode, Reaction]
    visited: bool
    
    def __init__(self, node: Node):
        self.original_node = node
        self.available_reactions = {
            reaction.code: reaction
            for reaction in node.reactions
        }
        self.visited = False

    def apply_reaction(self, reaction: Reaction) -> None:
        if reaction.single_use:
            self._lock_reaction(reaction)
    
    def _lock_reaction(self, reaction: Reaction) -> None:
        del self.available_reactions[reaction.code]
