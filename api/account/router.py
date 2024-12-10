from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse

from src.auth import security

router = APIRouter(
    prefix='/account',
    tags=['Account']
)

@router.get(
    path='/authorization',
    status_code=status.HTTP_200_OK,
    description='Авторизация по логину и хешу пароля'
)
@security.auth_required
async def GetAccount(
    user=Depends(security.get_current_user),
    target_user: int | None = Query(
        default=None, 
        description='ID целевого пользователя'
    )
) -> JSONResponse:
    """
    Получаем данные пользователя по токену.

    :param user: Данные текущего авторизованного пользователя.
    :param target_user: ID целевого пользователя (для администраторов или пользователей имеющих права).
    :return: Данные текущего пользователя или информация о целевом пользователе.
    """
    if target_user:
        # Логика обработки целевого пользователя
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Доступ разрешён к целевому пользователю", "target_user_id": target_user}
        )

    # Возврат данных текущего пользователя
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Доступ разрешён", "user": user}
    )