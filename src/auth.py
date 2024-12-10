from fastapi import Depends, HTTPException, status
from authx import AuthX, AuthXConfig

from src.config import config

__config__ = AuthXConfig(
    JWT_SECRET_KEY=config.SECRET_KEY,
    JWT_TOKEN_LOCATION=['headers'], 
    JWT_ALGORITHM='HS256'
)

security = AuthX(config=__config__)

def get_current_token(token: str = Depends(security.get_token_from_request)):
    try:
        user = security.verify_token(token=token)
        #TODO Проверка по BD
        return user  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Неверный токен'
        )
