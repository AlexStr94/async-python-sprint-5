import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


class AppSettings(BaseSettings):
    app_title: str = os.getenv('PROJECT_NAME', 'MyDisk')
    database_dsn: PostgresDsn
    project_host: str = os.getenv('PROJECT_HOST', '127.0.0.1')
    project_port: int = int(os.getenv('PROJECT_PORT', '8000'))
    api_v1_prefix: str = '/api/v1'
    secret_key: str = os.getenv(
        'SECRET_KEY',
        'a8e65ae1f66694950808f5318419a729c8576d2275f823edde47f7cc36a26d51'
    )
    echo = (os.getenv('ECHO', 'True') == 'True')
    

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')


app_settings = AppSettings() 