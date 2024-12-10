from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse

from authx import RequestToken
from src.auth import security, get_current_token

router = APIRouter(
    prefix='/account',
    tags=['Account']
)

@router.get(
    path='/authorization',
    status_code=status.HTTP_200_OK,
    description='Авторизация по логину и хешу пароля',
    dependencies=[
        Depends(security.get_token_from_request)
    ] 
)
async def GetAccount(
    current_user: RequestToken = Depends(get_current_token), 
    target_user: int | None = Query(
        default=None,
        description='ID целевого пользователя (для администраторов или пользователей, имеющих права)'
    )
) -> JSONResponse:
    """
    Получаем данные пользователя по токену.

    :param current_user: Данные текущего авторизованного пользователя, извлечённые из токена.
    :param target_user: ID целевого пользователя (для администраторов или пользователей, имеющих права).
    :return: Данные текущего пользователя или информация о целевом пользователе.
    """

    # Если передан target_user, добавляем дополнительную логику
    if target_user:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Доступ разрешён к целевому пользователю",
                "target_user_id": target_user
            }
        )

    # Возвращаем данные текущего пользователя
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Доступ разрешён", "user": current_user}
    )