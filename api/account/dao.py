from sqlalchemy import select, and_
from sqlalchemy.exc import NoResultFound

from dao.base import BaseDAO
from src.db import User, async_session_maker


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def authenticate_user(cls, login: str, password_hash: str):
        """
        Проверка логина и пароля пользователя
        """
        async with async_session_maker() as session:
            query = select(User).where(User.login == login)
            try:
                result = await session.execute(query)
                user = result.scalar_one()
            except NoResultFound:
                return None  # Пользователь не найден
            
            if user.password_hash != password_hash:
                return False  # Неверный пароль
            
            return user  