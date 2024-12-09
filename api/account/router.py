from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix='/account',
    tags=['Account']
)

@router.get(
    path='/authorization', 
    status_code=status.HTTP_200_OK, 
    dependencies=None, # TODO
    description='Авторизация по логину и хешу пароля'
)
async def GetAccount() -> JSONResponse:
    ... 