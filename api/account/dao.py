from sqlalchemy import select, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import NoResultFound, IntegrityError

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
        
    @classmethod
    async def register_user(cls, user: User):
        """
        Регистрация нового пользователя.
        """
        async with async_session_maker() as session:
            # Проверяем существование пользователя по логину
            result = await session.execute(select(User).filter_by(login=user.login))
            if result.scalar_one_or_none():
                return 'login_exists'
            
            # Проверяем существование пользователя по email
            result = await session.execute(select(User).filter_by(email=user.email))
            if result.scalar_one_or_none():
                return 'email_exists'

            session.add(user)
            try:
                await session.commit()
                return 'success'
            except IntegrityError:
                await session.rollback()
                return 'error'