import loguru
import sys
from config import config


def get_logger() -> "loguru.Logger":
    logger = loguru.logger
    logger.remove()
    
    format_pattern = '{time: YYYY-MM-DD HH:mm:ss} | {level} | {message}'

    if config.MODE == 'DEV':
        logger.add(
            sys.stdout,
            colorize=True,
            format=format_pattern,
            level='DEBUG',
        )
    
    if config.MODE == 'PROD':
        logger.add(
            config.LOG_PATH,
            rotation='5 MB',
            retention=3,
            compression='zip',
            enqueue=True,
            encoding='utf-8',
            level='DEBUG',
            format=format
        )

    return logger


logger = get_logger()
