from typing import Any

from pydantic import BaseModel, Field
from tg_quest.registry import REGISTRY

import logging 


logger = logging.getLogger('tg_quest.models.base')


GLOBAL_ENTITIES_COUNT: int = 0


def get_new_entity_code() -> str:
    global GLOBAL_ENTITIES_COUNT
    GLOBAL_ENTITIES_COUNT += 1
    return str(GLOBAL_ENTITIES_COUNT)


class BaseGameEntity(BaseModel, frozen=True):
    code: str = Field(default_factory=get_new_entity_code)

    def model_post_init(self, context: Any) -> None:
        entity_name = self.__class__.__name__
        if entity_name == "Node":
            logger.info('Node %s with code %s registered', self.content, self.code) # type: ignore
            REGISTRY.register_node(self) # type: ignore
        elif entity_name == "Reaction":
            logger.info('Reaction %s with code %s registered', self.title, self.code) # type: ignore
            REGISTRY.register_reaction(self) # type: ignore


type ContentType = str
type EntityCode = str
