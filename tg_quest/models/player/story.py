from collections.abc import Sequence
from dataclasses import dataclass

from tg_quest.models.story import Story
from tg_quest.models.base import EntityCode
from tg_quest.models.player.node import PlayerNode
from tg_quest.models.reaction import Reaction


@dataclass
class PlayerState:
    current_story: "PlayerStory"
    current_node: PlayerNode
    prev_node: PlayerNode | None
    last_turn_reaction: Reaction | None


@dataclass
class PlayerStory:
    origin_story: Story

    nodes: Sequence[PlayerNode]
    start_node: PlayerNode
    nodes_map: dict[EntityCode, PlayerNode]

    @classmethod
    def clone_from_story(cls, story: Story) -> "PlayerStory":
        nodes_map = {
            node.code: PlayerNode(node)
            for node in story.nodes
        }
        return cls(
            origin_story=story,
            nodes=tuple(nodes_map.values()),
            start_node=nodes_map[story.start_node.code],
            nodes_map=nodes_map
        )

    def get_initial_state(self) -> "PlayerState":
        return PlayerState(
            current_story=self,
            current_node=self.start_node,
            prev_node=None,
            last_turn_reaction=None
        )

    def get_node(self, code: EntityCode, trigger_reaction: Reaction | None = None) -> PlayerNode:
        player_node = self.nodes_map[code]
        if trigger_reaction and trigger_reaction.single_use:
            del player_node.available_reactions[trigger_reaction.code]
        return player_node
