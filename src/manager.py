# Основная логика
# делаем вывод через логер
# начинаем смотреть конфиг + проверяем его целостность
# подгружаем локализацию
# подключаемся к базе данных
# запускаем основные компоненты
# запускаем асинхронные функцию работающие в отдельном потоке
# ...

import time 
import pyotp 
import qrcode 
import io

from src.config import config, settings


class TwoFactor:
    def __init__(
        self, 
        secret_key: str = config.SECRET_KEY
    ) -> None:
        self.secret_key = secret_key
        self.totp = pyotp.TOTP(self.secret_key)

    async def generate_qr(
        self, 
        login: str, 
        issuer_name: str = settings.app.name
    ) -> bytes:
        """
        Генерирует QR-код в виде байтового объекта.
        :param username: Логин пользователя для привязки.
        :param issuer_name: Название издателя.
        :return: Байтовое представление PNG-изображения QR-кода.
        """
        uri = self.totp.provisioning_uri(
            name=login,
            issuer_name=issuer_name
        )

        qr_img = qrcode.make(uri)
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer.read()

    async def verify_code(self, code: str) -> bool:
        """
        Проверяет, является ли переданный код корректным.
        :param code: Код для проверки.
        :return: True, если код корректен; иначе False.
        """
        return self.totp.verify(code)