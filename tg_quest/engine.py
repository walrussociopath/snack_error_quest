import asyncio
import logging
from collections.abc import AsyncIterator

from tg_quest.models import Node
from tg_quest.registry import REGISTRY, Registry

logger = logging.getLogger("tg_quest.engine")


from tg_quest.models import Condition, Player, PlayerNode, Reaction, StoryRuntimeError


class StoryEngine:
    """Domain service responsible for resolving and executing story transitions."""

    def __init__(self, enable_wait: bool = True):
        self._enable_wait = enable_wait

    async def walk_to_node(
        self,
        new_node: PlayerNode,
        player: Player,
        reaction: Reaction | None = None
    ) -> AsyncIterator[PlayerNode]:
        """Advance player to the given node and automatically continue traversal until a node with available reactions
         is reached.

        Mutates player state. Yields each visited PlayerNode in order.
        """
        while True:
            player.move_to(new_node=new_node, reaction=reaction)
            yield player.current_node

            if new_node.available_reactions:
                return

            await self._try_to_sleep(new_node.original_node.wait)
            if next_node_code := new_node.original_node.next:
                new_node = player.story.get_node(next_node_code)
            else:
                raise StoryRuntimeError(f'Player node "{new_node.original_node.content} has no candidates to move."')

    def resolve_new_node_by_reaction(self, reaction: Reaction, player: Player) -> PlayerNode:
        node_code = self.resolve_new_node_code_by_reaction(reaction, player)
        return player.story.get_node(node_code, trigger_reaction=reaction)

    def resolve_new_node_code_by_reaction(self, reaction: Reaction, player: Player) -> str:
        if isinstance(reaction.next, str):
            return reaction.next

        elif isinstance(reaction.next, Condition):
            condition = reaction.next
            if condition.is_satisfied(player):
                return condition.next
            else:
                return condition.else_

        raise StoryRuntimeError(f'Reaction "{reaction.title}" was not transformed to Node change.')

    async def _try_to_sleep(self, seconds: float | None) -> None:
        if seconds is not None and self._enable_wait:
            await asyncio.sleep(seconds)

