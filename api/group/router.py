from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer  
from typing import Annotated
from sqlalchemy.future import select

from src.auth import create_access_token, get_current_user
from api.models import (
    UserStructure, GroupUsersStructure
)
from src.db import async_session_maker, GroupUsers
from api.group.dao import GroupDAO
from exceptions import GroupDeleteErrorException
from logger import _logger

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
        if groups := await GroupDAO.get_all(): 
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

    async with async_session_maker() as session:
        result = await session.execute(select(GroupUsers).filter_by(id=group_id))
        group = result.scalar_one_or_none()

        if group:
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
async def create_group(
    current_user: Annotated[UserStructure, Depends(get_current_user)],
    data: GroupUsersStructure
) -> JSONResponse:
    group = GroupUsers(name=data.name)
    group.set_rules(data.rules) 
    
    async with async_session_maker() as session:
        session.add(group)
        try:
            await session.commit() 
        except:
            await session.rollback() 
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'message': 'Не удалось создать группу'
                }
            ) 
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'Группа была успешно создана',
            'data': {
                'id': group.id,
                'name': group.name,
                'rules': group.rules
            }
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
    if await GroupDAO.update_group(nw_data):
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
    group = await GroupDAO.delete_group(group_id)
    if group:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Группа успешно удалена'}
        )
    elif group == False:
        _logger.error(GroupDeleteErrorException.detail, extra={
            'ActionError': GroupDeleteErrorException.__name__,
            'UserId': current_user.id
        })

        raise GroupDeleteErrorException
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Группа с указанным ID не найдена'}
        )
