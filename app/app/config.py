import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    AUTH_KEY: str = "qklfnONZ1517LOPENIKEkniknSJNd65262LKZOJND"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=values.get('POSTGRES_DB'),
        )

    STATICFILES_DIR: str = '/app/static'
    DATASETS_DIR: str = '/app/datasets'
    PREFIX_ENDPOINT: str = '/api'
    STATICFILES_ENDPOINT: str = '/api/static'

    class Config:
        case_sensitive = True
        env_file='.env'
        env_file_encoding='utf-8'


settings = Settings()

import os
if not os.path.exists(settings.STATICFILES_DIR):
    os.makedirs(settings.STATICFILES_DIR)
if not os.path.exists(settings.DATASETS_DIR):
    os.makedirs(settings.DATASETS_DIR)