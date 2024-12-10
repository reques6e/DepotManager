from pydantic import BaseModel
from datetime import datetime


class UserStructure(BaseModel):
    id: int | None = None
    login: str
    name: str
    surname: str
    email: str
    phone_number: str
    group_id: int  # ID группы (например: Администраторы, Курьеры, Бухгалтеры)
    city_id: int
    prefix: str
    password_hash: str  # Хеш пароля, сами пароли не храним
    status: str | None = None
    two_factor: bool = False
    is_blocked: bool = False
    requires_password_reset: bool = False  # Нужно ли сменить пароль при следующем входе
    created_at: datetime


class CityStructure(BaseModel):
    id: int | None = None
    name: str  # Например: Гудаута
    country: str  # Например: Абхазия


class GroupUsersStructure(BaseModel):
    id: int | None = None
    name: str
    rules: list[int]
