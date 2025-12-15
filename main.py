import asyncio
from os import getenv

print('sad import')
from tg_quest import Quest
import logging

logger = logging.getLogger('tg_quest')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


from game_content.ядерный_похмельник.история_вани import ИСТОРИЯ_ВАНИ


API_TOKEN = getenv('API_TOKEN')
progress_expired_message = (
    "Твой прогресс был сброшен из-за долгого отсутствия :-(\n"
    "Придётся начать сначала... /start"
)


quest = Quest(
    story=ИСТОРИЯ_ВАНИ,
    api_token=API_TOKEN ,
    progress_expired_message=progress_expired_message,
    ttl_hours=24*3,
    disable_wait=True,
    
)

async def main() -> None:
    await quest.start_polling()



if __name__ == '__main__':
    print('already')
    asyncio.run(main())
