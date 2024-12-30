from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from authx import RequestToken
from src.auth import security, get_current_token

from src.db import DataBase

database = DataBase()

router = APIRouter(
    prefix='/account',
    tags=['Account']
)

@router.get(
    path='/authorization',
    status_code=status.HTTP_200_OK,
    description='Авторизовывает пользователя'
)
async def authorization(
    login: str = Query(..., description='Логин пользователя'),
    hash_password: str = Query(..., description='Зашифрованный пароль пользователя')
) -> JSONResponse:
    """
    Эндпоинт для авторизации пользователя по логину и паролю. 
    Пользователь должен предоставить свой логин и зашифрованный пароль в запросе. 
    Если данные корректны, возвращается успешный ответ с токеном авторизации.
    
    **Параметры запроса:**
    - `login`: Логин пользователя (строка).
    - `hash_password`: Зашифрованный пароль пользователя (строка).

    **Пример ответа от сервера при успешной авторизации:**
    - `200` - Авторизация прошла успешно

    ```js 
    {
        'message': 'Авторизация прошла успешно', 
        'data': {
            'id': user_data.id,
            'login': user_data.login,
            'token': jwt_token
        }
    }
    ```

    **Пример ответа от сервера при не успешной авторизации:**
    - `401` - Не авторизован

    ```js 
    {
        'message': 'Неверный логин или пароль'
    }
    ```
    """

    if user_data := await database.authenticate_user(
        login=login,
        password_hash=hash_password
    ):
        jwt_token = security.create_access_token(uid=hash_password, user_id=user_data.id)

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
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'message': 'Неверный логин или пароль'
            }
        )

@router.get(
    path='/me',
    status_code=status.HTTP_200_OK,
    description='Получение информации о себе',
)
async def get_my_account(
    request: Request,  # Передаем Request напрямую
    current_user=Depends(get_current_token),
    target_user: int | None = Query(
        default=None,
        description='ID целевого пользователя (для администраторов или пользователей, имеющих права)'
    )
) -> JSONResponse:
    """

    """

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": current_user.id}
    )