from fastapi import Depends, HTTPException, status
from authx import AuthX, AuthXConfig

from src.config import config

__config__ = AuthXConfig(
    JWT_SECRET_KEY=config.SECRET_KEY,
    JWT_TOKEN_LOCATION=['headers'], 
    JWT_ALGORITHM='HS256'
)

security = AuthX(config=__config__)

async def get_current_token(token: str = Depends(security.get_access_token_from_request)):
    """
    Проверяет валидность токена и извлекает данные пользователя.

    :param token: JWT-токен, извлечённый из заголовков.
    :return: Данные пользователя, содержащиеся в токене.
    """
    try:
        payload = security.verify_token(token)
        return payload  # Возвращаем данные из токена
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен или истёк срок действия",
            headers={"WWW-Authenticate": "Bearer"},
        )