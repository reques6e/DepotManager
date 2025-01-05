from typing import Literal

# Данный импорт работал на первой ветке pydantic.
# from pydantic import BaseSettings

from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Типизация для подключения базы данных
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f'mysql+asyncmy://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}'
    
    # Секретный ключ, нужен для генерации JWT токенов и 
    # т.д
    SECRET_KEY: str

    @property
    def SECRET_JWT_KEY(self):
        return f'{self.SECRET_KEY}'

    # Отправка писем по SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

settings = Settings()
