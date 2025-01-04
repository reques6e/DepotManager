try:
    import uvicorn
    import asyncio
    import logging

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.openapi.utils import get_openapi
    from fastapi.security import OAuth2PasswordBearer
except ImportError:
    def main() -> None:
        import sys

        print(
            'Библиотеки не установлены.'
            'В терминал нужно прописать:\n'
            'pip3 install -r requirements.txt'
        )
        sys.exit(1)

    main()

from api.account.router import router as router_account 
from api.group.router import router as router_group 
# from data.response.exceptions import FastAPIExceptionHandlers

logging.basicConfig(level=logging.WARNING)  
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

api = FastAPI(
    title='API By Reques6e',
    version='0.1.0',
    redoc_url=None,
    openapi_tags=[
        {
            "name": "Account",
            "description": "Эндпоинты для работы с учетной записью пользователя."
        }
    ],
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Разрешаем доступ с фронтенда
    allow_credentials=True,
    allow_methods=['GET', 'POST'],  #
    allow_headers=['*'],  
)

# FastAPIExceptionHandlers(api)

api.include_router(router_account)
api.include_router(router_group)

api.openapi_schema = get_openapi(
    title="API By Reques6e",
    version="0.1.0",
    description="API для работы с учетными записями пользователей",
    routes=api.routes,
)

api.openapi_schema["components"]["securitySchemes"] = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}

api.openapi_schema["security"] = [{"BearerAuth": []}]

if __name__ == '__main__':
    uvicorn.run(
        app='app:api', 
        host='0.0.0.0', 
        port=91,
        reload=True # В проде офнуть нужно
    )
