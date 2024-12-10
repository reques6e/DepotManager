try:
    import uvicorn
    import asyncio

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
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
# from data.response.exceptions import FastAPIExceptionHandlers

api = FastAPI(
    title='API By Reques6e',
    version='0.1.0',
    redoc_url=None
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


if __name__ == '__main__':
    uvicorn.run(
        app='app:api', 
        host='0.0.0.0', 
        port=91,
        reload=True # В проде офнуть нужно
    )