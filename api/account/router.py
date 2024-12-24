from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from authx import RequestToken
from src.auth import security, get_current_token

router = APIRouter(
    prefix='/account',
    tags=['Account']
)

@router.get(
    path='/test',
    status_code=status.HTTP_200_OK,
    description='Выдаёт тестовый ключ'
)
async def Generate_test_token() -> JSONResponse:
    """
    Тестовый метод

    Выдаёт токен для работы с API
    """
    tk = security.create_access_token(uid='12312312')

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'message': 'Тестовый токен', 'token': tk}
    )

@router.get(
    path='/authorization',
    status_code=status.HTTP_200_OK,
    description='Авторизация по логину и хешу пароля',
)
async def GetAccount(
    request: Request,  # Передаем Request напрямую
    current_user=Depends(get_current_token),
    target_user: int | None = Query(
        default=None,
        description='ID целевого пользователя (для администраторов или пользователей, имеющих права)'
    )
) -> JSONResponse:
    """
    Получаем данные пользователя по токену.

    :param request: HTTP-запрос.
    :param current_user: Данные текущего авторизованного пользователя, извлечённые из токена.
    :param target_user: ID целевого пользователя (для администраторов или пользователей, имеющих права).
    :return: Данные текущего пользователя или информация о целевом пользователе.
    """

    if target_user:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Доступ разрешён к целевому пользователю",
                "target_user_id": target_user
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Доступ разрешён"}
    )