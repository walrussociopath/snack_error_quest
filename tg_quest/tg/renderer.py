


from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_quest.models.base import EntityCode
from tg_quest.models.player.node import PlayerNode
from tg_quest.registry import REGISTRY
from tg_quest.tg.progress import TGPlayer


class Renderer:
    def __init__(self):
        self._reaction_buttons: dict[EntityCode, InlineKeyboardButton] = {}
        self.cache_inline_buttons()

    def cache_inline_buttons(self) -> None:
        for reaction in REGISTRY.reactions.values():
            print(f"cache {reaction}")
            button = InlineKeyboardButton(text=reaction.title, callback_data=reaction.code)
            self._reaction_buttons[reaction.code] = button

    def render_keyboard(self, node: PlayerNode) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [self._reaction_buttons[code]]
                for code in node.available_reactions.keys()
            ]
        )

    def render_node(self, node: PlayerNode, player: TGPlayer) -> dict[str, Any]:
        return {
            "text": node.original_node.content,
            "reply_markup": self.render_keyboard(node) if node.available_reactions else None
        }

    def render_current_node(self, player: TGPlayer) -> dict[str, Any]:
        return self.render_node(
            player.current_node,
            player
        )
