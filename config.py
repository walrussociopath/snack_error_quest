from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    API_TOKEN: str
    MODE: Literal['PROD', 'DEV'] = 'PROD'
    LOG_PATH: str = 'log.log'


config = Config()
