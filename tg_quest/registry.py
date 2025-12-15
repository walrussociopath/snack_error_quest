from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tg_quest.models import EntityCode, Node, Reaction


class Registry:
    def __init__(self):
        self.nodes: dict[EntityCode, Node] = {}
        self.reactions: dict[EntityCode, Reaction] = {}

    def register_node(self, node: "Node") -> None:
        self.nodes[node.code] = node

    def register_reaction(self, reaction: "Reaction") -> None:
        self.reactions[reaction.code] = reaction


# Yeah. Global registry!
REGISTRY = Registry()
