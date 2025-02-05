import jwt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from typing import Annotated


from api.models import UserStructure
from api.account.dao import UserDAO

from src.manager import UserManager
from src.logger import _logger

from config import settings
from exceptions import UserIsBlocked, FailCheckUserData

ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserStructure:
    """
    Извлекает текущего пользователя на основе токена авторизации.
    
    Пытается декодировать токен и извлечь идентификатор пользователя. 
    Если токен недействителен или пользователь не найден, вызывает исключение 401 (Unauthorized).
    
    Args:
        token (str): Токен авторизации, переданный в заголовке запроса.
    
    Returns:
        UserStructure: Модель пользователя, если токен валиден.
    
    Raises:
        HTTPException: В случае ошибки валидации токена или отсутствии пользователя.
    """
    
    try:
        payload = jwt.decode(token, settings.SECRET_JWT_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('id')
        if user_id is None:
            raise FailCheckUserData
    except InvalidTokenError:
        raise FailCheckUserData

    user = await UserDAO.find_one_or_none(id=user_id)
    if user is None:
        raise FailCheckUserData
    
    validate = await UserManager.validate_user(user=user)
    if validate.result == False:
        raise UserIsBlocked

    return user


async def decode_jwt(token: str) -> dict:
    """
    Декодирует JWT токен и извлекает из него полезную нагрузку.
    
    Эта функция предназначена для декодирования токенов и обработки ошибок, 
    таких как истечение срока действия или недействительный токен.

    Args:
        token (str): JWT токен для декодирования.

    Returns:
        dict: Полезная нагрузка (payload) из токена.

    Raises:
        HTTPException: В случае истечения срока действия токена или других ошибок.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_JWT_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired.',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token.',
            headers={'WWW-Authenticate': 'Bearer'},
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает новый JWT токен с заданными данными и временем истечения.

    Если время истечения не указано, токен будет действителен 30 дней.

    Args:
        data (dict): Данные, которые будут зашифрованы в токене (например, идентификатор пользователя).
        expires_delta (Optional[timedelta]): Время истечения токена. Если не указано, токен истекает через 30 минут.

    Returns:
        str: Сгенерированный JWT токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt
