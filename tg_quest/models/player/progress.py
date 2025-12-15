from tg_quest.models.player.story import PlayerStory
from tg_quest.models.player.node import PlayerNode
from tg_quest.models.reaction import Reaction
from tg_quest.models.story import Story


class Player:
    def __init__(self, story: Story):
        self.story = PlayerStory.clone_from_story(story)
        self.state = self.story.get_initial_state()
        self.items = []

    @property
    def current_node(self) -> PlayerNode:
        return self.state.current_node

    def _set_current_node(self, current_node: PlayerNode, reaction: Reaction | None = None) -> None:
        self.current_node.visited = True
        self.state.prev_node = self.current_node
        self.state.current_node = current_node

    def move_to(self, new_node: PlayerNode, reaction: Reaction | None = None):     
        if reaction:
            self.current_node.apply_reaction(reaction)   
        self._set_current_node(new_node)
