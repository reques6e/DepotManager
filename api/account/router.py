from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer  
from typing import Annotated
from datetime import datetime

from src.db import User, async_session_maker

from sqlalchemy.future import select

from src.auth import create_access_token, get_current_user
from api.models import UserStructure
from api.account.dao import UserDAO
from exceptions import (
    UserCreateErrorException, 
    UserLoginAlreadyExistsException,
    UserEmailAlreadyExistsException
)
from logger import _logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix='/account',
    tags=['Account']
)

@router.post(
    path='/registration',
    status_code=status.HTTP_201_CREATED,
    description='Регистрация нового пользователя'
)
async def registration(
    login: str = Body(..., description='Логин пользователя'),
    name: str = Body(..., description='Имя пользователя'),
    surname: str = Body(..., description='Фамилия пользователя'),
    email: str = Body(..., description='Электронная почта пользователя'),
    phone_number: str = Body(..., description='Номер телефона пользователя'),
    password: str = Body(..., description='Пароль пользователя'),
    group_id: int = Body(..., description='ID группы пользователя'),
    city_id: int = Body(..., description='ID города пользователя'),
    prefix: str = Body(..., description='Префикс для пользователя')
) -> JSONResponse:
    """
    Регистрация нового пользователя.
    """
    user = User(
        login=login,
        name=name,
        surname=surname,
        email=email,
        phone_number=phone_number,
        group_id=group_id,
        city_id=city_id,
        prefix=prefix,
        password_hash=password,
        created_at=datetime.utcnow(),
        status='active',
        two_factor=False,
        is_blocked=False,
        requires_password_reset=False
    )

    async with async_session_maker() as session:
        result = await session.execute(select(User).filter_by(login=login))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            _logger.error(UserLoginAlreadyExistsException.detail, extra={
                'ActionError': UserLoginAlreadyExistsException.__name__,
                'login': login
            })

            raise UserLoginAlreadyExistsException

        result = await session.execute(select(User).filter_by(email=email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            _logger.error(UserEmailAlreadyExistsException.detail, extra={
                'ActionError': UserEmailAlreadyExistsException.__name__,
                'email': email
            })
            raise UserEmailAlreadyExistsException
        
        # Временная затычка
        session.add(user)
        try:
            await session.commit()
        except:
            await session.rollback()
            _logger.error(UserCreateErrorException.detail, extra={
                'ActionError': UserCreateErrorException.__name__
            })

            raise UserCreateErrorException

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'message': 'Пользователь успешно зарегистрирован'}
    )

@router.get(
    path='/authorization',
    status_code=status.HTTP_200_OK,
    description='Авторизовывает пользователя'
)
async def authorization(
    login: str = Query(..., description='Логин пользователя'),
    password: str = Query(..., description='Пароль пользователя')
) -> JSONResponse:
    """
    Эндпоинт для авторизации пользователя по логину и паролю. 
    Пользователь должен предоставить свой логин и пароль в запросе. 
    Если данные корректны, возвращается успешный ответ с токеном авторизации.
    """

    user_data = await UserDAO.authenticate_user(login=login, password_hash=password)

    if not user_data:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'message': 'Неверный логин или пароль'}
        )

    jwt_token = create_access_token(
        data={
            'id': user_data.id
        }
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'Авторизация прошла успешно',
            'data': {
                'id': user_data.id,
                'login': user_data.login,
                'token': jwt_token
            }
        }
    )

@router.get(
    path='/me',
    status_code=status.HTTP_200_OK,
    description='Получение информации о себе'
)
async def get_my_account(
    current_user: Annotated[UserStructure, Depends(get_current_user)]
) -> JSONResponse:
    """
    Эндпоинт для получения информации о себе.

    :param current_user: Данные текущего пользователя.
    :return: Информация о пользователе.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'Информация была успешно получена',
            'data': {
                'id': current_user.id,
                'login': current_user.login,
                'name': current_user.name,
                'surname': current_user.surname,
                'email': current_user.email,
                'phone_number': current_user.phone_number,
                'group_id': current_user.group_id,
                'city_id': current_user.city_id,
                'prefix': current_user.prefix,
                'status': current_user.status,
                'two_factor': current_user.two_factor,
                'is_blocked': current_user.is_blocked,
                'requires_password_reset': current_user.requires_password_reset,
                'created_at': str(current_user.created_at),
            }
        }
    )

@router.put(
    path='/me',
    status_code=status.HTTP_200_OK,
    description='Обновляет информацию своего профиля'
)
async def get_my_account(
    current_user: Annotated[UserStructure, Depends(get_current_user)],
    new_data: UserStructure = Body(..., description='Новые данные пользователя')
) -> JSONResponse:
    ...