from authx import AuthX, AuthXConfig
from src.config import config

__config__ = AuthXConfig()
__config__.JWT_SECRET_KEY = config.SECRET_KEY

security = AuthX(config=__config__)