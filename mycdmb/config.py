""Pydantic Settings — DB / JWT / Auth 配置"""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    APP_NAME: str = 'MyCDMB'
    APP_VERSION: str = '1.0.0'

    # 数据库
    SQLALCHEMY_DATABASE_URL: str = 'sqlite:///./mycdmb.db'

    # JWT
    SECRET_KEY: str = 'change-me-in-production'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Bootstrap
    BOOTSTRAP_ADMIN_USERNAME: str = 'admin'
    BOOTSTRAP_ADMIN_PASSWORD: str = 'admin123'

    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).resolve().parent.parent


settings = Settings()
