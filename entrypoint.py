from os import getenv
import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from src.core.logger import logger


async def main() -> None:
    from src.core.player_progress import init_in_memory_progress_storage
    init_in_memory_progress_storage()

    from src.core.handlers import link_story_to_handlers
    link_story_to_handlers()

    bot = Bot(token=config.API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    
    from src.core.dispatcher import dp 
    
    logger.info('Bot started')

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
