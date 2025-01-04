from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer  
from typing import Annotated

from src.auth import create_access_token, get_current_user
from api.models import (
    UserStructure, GroupUsersStructure
)
from src.db import DataBase

database = DataBase()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix='/group',
    tags=['Group']
)

@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    description='Получает все группы или список всех групп'
)
async def get_group(
    current_user: Annotated[UserStructure, Depends(get_current_user)],
    group_id: int | None = None
) -> JSONResponse:
    if group_id is None:
        if groups := await database.get_all_groups(): 
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    'message': 'Список групп был получен успешно',
                    'data': groups 
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'message': 'Не удалось найти группы'
                }
            )


    if group := await database.get_group(
        group_id=group_id
    ):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'Информация о группе была успешно получена',
                'data': {
                    'id': group.id,
                    'name': group.name,
                    'rules': group.rules
                }
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': 'Не удалось найти группу'
            }
        )

@router.post(
    path='/',
    status_code=status.HTTP_200_OK, 
    description='Создает группу'
)
async def update_group(
    current_user: Annotated[UserStructure, Depends(get_current_user)],
    data: GroupUsersStructure
) -> JSONResponse:
    if result := await database.create_group_user(group_data=data):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'Группа была успешно создана',
                'data': {
                    'id': result.id,
                    'name': result.name,
                    'rules': result.rules
                }
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': 'Не удалось создать группу'
            }
        )

@router.put(
    path='/',
    status_code=status.HTTP_200_OK, 
    description='Обновляет данные группы'
)
async def update_group(
    current_user: Annotated[UserStructure, Depends(get_current_user)],
    nw_data: GroupUsersStructure
) -> JSONResponse:
    if await database.update_group(nw_data):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'Данные группы успешно обновлены'
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': 'Не удалось обновить данные группы'
            }
        )

@router.delete(
    path='/',
    status_code=status.HTTP_200_OK,
    description='Удаляет группу по ID'
)
async def delete_group(
    current_user: Annotated[UserStructure, Depends(get_current_user)],
    group_id: int = Query(..., description='ID группы для удаления')
) -> JSONResponse:
    if await database.delete_group(group_id):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Группа успешно удалена'}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Группа с указанным ID не найдена'}
        )
