from abc import ABC, abstractmethod
from enum import StrEnum
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F
from typing import Any, ClassVar, Iterable, Protocol, Sequence, Union, Iterator
from dataclasses import dataclass, field
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter
from uuid import uuid4

from src.core.logger import logger
from src.core.player_progress import player_progress
from src.core.conditions import Condition


REACTIONS_COUNT = 0

def _get_reaction_index() -> str:
    global REACTIONS_COUNT
    REACTIONS_COUNT += 1
    return str(REACTIONS_COUNT)


@dataclass
class Reaction:
    """Реакция."""

    # Текст реакции
    title: str

    # Нода, на которую переходим после реакции
    next: str

    # Убирает реакцию из ноды, в которой была применена эта реакция
    lock_after_use: bool | None = None 

    _callback_index: str = field(default_factory=_get_reaction_index) 

    REGISTRY: ClassVar[dict[str, "Reaction"]] = {}

    class _CallbackData(CallbackData, prefix='cb'):
        index: str

    def __post_init__(self) -> None:
        self.REGISTRY[self._callback_index] = self
        self._callback_data = Reaction._CallbackData(index=self._callback_index)
        self._callback_data_packed = self._callback_data.pack()

        self._inline_button = InlineKeyboardButton(
            text=self.title,
            callback_data=self._callback_data_packed
        )
        self._filter = self._callback_data.filter(F.index == self._callback_data.index)

    @property
    def inline_button(self) -> InlineKeyboardButton:
        return self._inline_button 

    @property
    def filter(self) -> CallbackQueryFilter:
        return self._filter

    @classmethod
    def get_by_index(cls, index: str) -> Union["Reaction", None]:
        return cls.REGISTRY.get(index)


@dataclass
class SubstoryRoute:
    title: str
    story: "AbstractStory"


class Directions(StrEnum):
    """Сервисные ноды."""

    # Вернуться на ноду назад
    BACK = 'Назад'


class Item:
    """Предмет."""
    name: str


@dataclass
class Node:
    """Точка на отрезке истории. В каком-то смысле может быть локацией. """

    # То, что будет отправлено игроку при переходе на эту ноду.
    content:  str

    # Код точки. Можно указать любую строку. Код должен быть уникальным для истории.
    code: str = field(default_factory=lambda: str(uuid4()))

    # Возможные реакции в InlineButton
    reactions: Sequence[Reaction] = field(default_factory=tuple)
    
    # Подождать столько секунд перед тем как переходить на следующую ноду. Доступно только если reactions=None и next
    # установлено.
    wait: float | None = None 
    
    # Следующая нода, если не установлены reactions. Либо, если все возможные реакции заблокированы. Например из-за
    # Reaction.drop_if_used
    next: str | Condition | None = None
    
    # Терминальная точка. Заканчивает историю. Возвращает управление на уровень выше.
    is_terminal: bool = False

    # Предложить игроку применить предмет в ноде. reactions построются на основе инвентаря пользователя дополняя
    # реакции из self.reactions
    ask_using_item: bool = True

    # Добавить кнопку назад, возвращающую игрока в предыдущую ноду
    can_go_back: bool = False

    # Описание переходов на ноды при применении предметов на локации. str здесь - код ноды
    items_transition: dict[Item, Union[str, "Node"]] | None = None

    # Предметы добавляются в инвентарь сразу же при переходе на ноду.
    add_items: Sequence[Item] | Item | None = None

    # Является ли нода стартовой в истории
    is_start_node: bool = False

    @property
    def reactions_keyboard(self) -> InlineKeyboardMarkup:
        reaction_buttons: list[list[InlineKeyboardButton]] = []
        player_progress_ = player_progress.get()
        for reaction in self.reactions:
            if reaction.lock_after_use and reaction in player_progress_.selected_reactions:
                continue
            reaction_buttons.append([reaction.inline_button])
        return InlineKeyboardMarkup(
            inline_keyboard=reaction_buttons
        )

    @property
    def message_kwargs(self) -> dict[str, Any]:
        # Возвращаемый dict должен соответствовать сингатуре aiogram.types.Message.answer
        return {
            **self._render_text_attrs(),
            'reply_markup': self.reactions_keyboard if self.reactions else None
        }

    def has_reactions(self) -> bool:
        return len(self.reactions) > 0

    def needs_a_pause(self) -> bool:
        return isinstance(self.wait, float) and self.wait > 0

    def _render_text_attrs(self) -> dict[str, Any]:
        return {
            'text': self.content
        }


class ItemApplication(Node):
    """Нода применения предмета."""

    # Удалить предмет из инвентаря после применения
    lose_after_use: bool = False


class AbstractStory(ABC):
    # TODO(@walrussociopath): Пофиксить LSP

    def __init__(self, code: str, start_node: Node, nodes_map: dict[str, Node]):
        self.code = code
        self._start_node = start_node
        self.nodes_map = nodes_map

    @abstractmethod
    def get_start_node(self, node: Node | None = None) -> Node:
        pass

    @property
    def start_node(self) -> Node:
        return self.get_start_node()        

    def get_next_node_by_reaction(self, reaction_callback: Reaction._CallbackData) -> Node:
        reaction = Reaction.get_by_index(reaction_callback.index)
        if reaction is None:
            # TODO: Тут конечно по такому логу будет тяжело что-то понять
            raise ValueError(f'Реакция {reaction_callback.index} не найдена')
        return self.nodes_map[reaction.next]

    def get_next_node_by_node(self, node: Node) -> Node:
        if node.next is None:
            if not node.is_terminal:
                raise ValueError('У ноды нет следующего пути, при этом она не является терминальной!')
            return self.get_start_node(node)
        return self.nodes_map[node.next]

    def iter_reactions(self) -> Iterator[Reaction]:
        for node in self.nodes_map.values():
            yield from node.reactions


class Story(AbstractStory):

    @classmethod
    def from_nodes(cls, nodes: Sequence[Node], code: str) -> "Story":
        start_node, nodes_map = cls.parse_content(code, nodes)
        return cls(code, start_node, nodes_map)
        
    @classmethod
    def parse_content(cls, code: str, nodes: Sequence[Node]) -> tuple[Node, dict[str, Node]]:
        _start_node: Node | None = None
        _nodes_map: dict[str, Node] = {}

        for node in nodes:
            node.code = f'{code}_{node.code}'
            if node.next:
                node.next = f'{code}_{node.next}'
            cls._add_prefix_to_reactions_nodes(code, node)
            if node.code in _nodes_map.keys():
                raise ValueError(f'Нода с кодом "{node.code}" уже есть в истории {code}')
            _nodes_map[node.code] = node
            if node.is_start_node:
                if _start_node is not None:
                    raise ValueError(f'В истории {code} уже есть стартовая нода {_start_node}. Конфликт'
                                     f' с нодой {node.code}')
                _start_node = node

        if _start_node is None:
            raise ValueError(f'Не было найдено стартовой ноды для истории {code}')

        return _start_node, _nodes_map

    @staticmethod
    def _add_prefix_to_reactions_nodes(code: str, node: Node) -> None:
        for reaction in node.reactions:
            reaction.next = f'{code}_{reaction.next}'

    def get_start_node(self, node: Node | None = None) -> Node:
        if start_node := self._start_node:
            return start_node
        raise AttributeError('Стартовая нода не установлена')

    def __str__(self) -> str:
        return self.__repr__() 

    def __repr__(self) -> str:
        return (
            'Story('
                f'code={self.code.__repr__()},' 
                f'start_node={self._start_node.__repr__()},'
                f'nodes_map={self.nodes_map.__repr__()}'
            ')'
        )
    

class StoryRouter(AbstractStory):

    def __init__(
        self, 
        code: str, 
        start_node: Node, 
        nodes_map: dict[str, Node], 
        node_story_map: dict[str, AbstractStory] | None = None,
        substories = None
    ):
        super().__init__(code, start_node, nodes_map)
        if node_story_map:
            self._node_story_map = node_story_map
        else:
            self._node_story_map: dict[str, AbstractStory] = {}
        self._substories = substories
        self.REACTIONS_REGISTRY: tuple[Reaction, ...] = tuple(self.iter_reactions())

    @classmethod
    def from_stories(cls, code: str, content: str, routes: Sequence[SubstoryRoute]) -> "StoryRouter":
        start_node = cls.create_start_node(code, content, routes)
        nodes_map = cls.create_nodes_map(code, routes)
        nodes_map[start_node.code] = start_node
        node_story_map = cls.create_node_story_map(routes)
        substories = [route.story for route in routes]
        story = cls(code, start_node, nodes_map, node_story_map, substories)
        return story

    @classmethod
    def create_nodes_map(
        cls,
        code: str,
        routes: Sequence[SubstoryRoute]
    ) -> dict[str, Node]:
        nodes_map: dict[str, Node] = {}
        for route in routes:
            nodes_map |= route.story.nodes_map
        return nodes_map

    @classmethod
    def create_start_node(cls, code: str, content: str, routes: Sequence[SubstoryRoute]) -> Node:
        start_node =  Node(
            code=code,
            content=content,
            reactions=tuple(
                Reaction(
                    title=route.title,
                    next=route.story.get_start_node().code
                )
                for route in routes
            )
        )
        return start_node

    @classmethod
    def create_node_story_map(cls, routes: Sequence[SubstoryRoute]) -> dict[str, AbstractStory]:
        node_story_map: dict[str, AbstractStory] = {}
        for route in routes:
            for node in route.story.nodes_map.values():
                node_story_map[node.code] = route.story
        return node_story_map

    def get_start_node(self, node: Node | None = None) -> Node:
        if node is None:
            return self._start_node
        return self._node_story_map[node.code].get_start_node(node)

    def iter_reactions(self) -> Iterator[Reaction]:
        yield from self.start_node.reactions
        for story in self._substories:
            yield from story.iter_reactions()
