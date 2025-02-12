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
import os
import aiohttp
import uuid as uuid_generate

from datetime import datetime
from packaging.version import Version as _versionCompare

from api.models import UserStructure
from src.db import Attachment, async_session_maker
from src.s3 import _S3Connector, _S3Config
from config import settings


class TwoFactor:
    def __init__(
        self, 
        secret_key: str = settings.SECRET_KEY
    ) -> None:
        self.secret_key = secret_key
        self.totp = pyotp.TOTP(self.secret_key)

    async def generate_qr(
        self, 
        login: str, 
        issuer_name: str = settings.AppName
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
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer.read()

    async def verify_code(self, code: str) -> bool:
        """
        Проверяет, является ли переданный код корректным.
        :param code: Код для проверки.
        :return: True, если код корректен; иначе False.
        """
        return self.totp.verify(code)


class SystemManager:
    __app_version__ = '0.1 Alpha'

    def __init__(self):
        pass

    async def check_updates(self) -> bool:
        """Проверка обновлений"""
        async with aiohttp.ClientSession() as session:
            # В URL указан тестовый сервер, ожидается ответ в таком формате:
            # {"version": "0.2 Beta"}
            async with session.get(
                url='https://depot.repo.reques6e.ru/version'
            ) as response:
                if response.status == 200:
                    latest_version = await response.json()['version']
                    if _versionCompare(latest_version) > _versionCompare(__class__.__app_version__):
                        return True

                return False


class OperationResult:
    def __init__(
        self, 
        result: bool = False, 
        message: str | None = None
    ) -> None:
        self.result = result
        self.message = message


S3Data = _S3Config(
    bucket_name=settings.S3_BUCKET_NAME,
    endpoint_url=settings.S3_ENDPOINT_URL,
    region_name=settings.S3_REGION_NAME,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY
)


class AttachmentType:
    FILE: str = 'file'
    VIDEO: str = 'video'
    PHOTO: str = 'photo'
    AUDIO: str = 'audio'
    DOCUMENT: str = 'document'
    ARCHIVE: str = 'archive'


class FileObj:
    def __init__(
        self,
        name: str | None,
        extension: str,
        attachment_type: str | None = AttachmentType.FILE
    ):
        self.name = name
        self.extension = extension
        self.attachment_type = attachment_type


    def __str__(self) -> str:
        """Return full file name"""
        return f'{self.name}.{self.extension}'


class AttachmentManager:
    def __init__(self):
        pass

    def file_url(self, file_name):
        return f'{S3Data.endpoint_url}/{S3Data.bucket_name}/{file_name}'

    @staticmethod
    async def upload(
        file_name: str, 
        file_content: bytes
    ) -> FileObj:
        uuid = uuid_generate.uuid4()
        file_extension = os.path.splitext(file_name)[1].lstrip('.')
        obj = FileObj(
            name=uuid, 
            extension=file_extension,
            attachment_type=AttachmentType.FILE
        )
        full_file_name = obj.__str__()

        file_stream = io.BytesIO(file_content)
        
        async with _S3Connector(S3Data) as s3:
            await s3.upload_fileobj(
                fileobj=file_stream, 
                key=full_file_name
            )
        
        attachment_data = Attachment(
            uuid=uuid,
            file_path=full_file_name,
            attachment_type='file',
            file_extension=file_extension
        )

        async with async_session_maker() as session:
            session.add(attachment_data)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()

        return obj


class UserManager:
    def __init__(self):
        pass
    
    @staticmethod
    async def validate_user(
        user: UserStructure
    ) -> OperationResult:
        """
        Проверка пользователя на блокировки.
        :param user: Информация о пользователе.
        :return: True - пользователь не имеет ни каких блокировок/ограничений
        """

        if user.is_blocked:
            return OperationResult(False, 'is_blocked')
        
        return OperationResult(True)

    @staticmethod
    async def get_user_full_name(
        user: UserStructure
    ) -> str:
        """
        Получение полного имени пользователя.
        :param user: Информация о пользователе.
        :return: Полное имя пользователя в формате "Фамилия Имя".
        """
        return f"{user.surname} {user.name}"

    @staticmethod
    async def check_two_factor_auth(
        user: UserStructure
    ) -> bool:
        """
        Проверка, активирована ли двухфакторная аутентификация у пользователя.
        :param user: Информация о пользователе.
        :return: True, если двухфакторная аутентификация активирована.
        """
        return user.two_factor

    @staticmethod
    async def update_fio(
        user: UserStructure, 
        name: str,
        surname: str
    ) -> bool | UserStructure:
        """
        Обновление имени пользователя и фамилии.
        :param user: Информация о пользователе.
        :param name: Имя пользователя
        :param surname: Фамилия пользователя
        :return: Обновлённый объект пользователя.
        """

        # Проверка длины имени
        if len(name) > 30: 
            return False

        # Проверка длины фамилии
        if len(surname) > 30: 
            return False
        
        return user
        
    @staticmethod
    async def update_phone_number(
        user: UserStructure, 
        phone_number: str
    ) -> bool | UserStructure:
        """
        Обновление номера телефона пользователя.
        :param user: Информация о пользователе.
        :param phone_number: Новый номер телефона. (Обязательно с +)
        :return: Обновлённый объект пользователя.
        """
        # Проверка на наличие "+" в начале номера
        if not phone_number.startswith("+"):
            return False

        # Проверка на отсутствие букв
        if not phone_number[1:].isdigit():
            return False

        # Проверка длины номера
        # if len(phone_number) != 12:
        #     ...

        # TODO
        # Нужно добавить проверку, 1 номер = 1 юзер.
        # На каждый аккаунт должен быть свой уникальный
        # номер телефона

        user.phone_number = phone_number
        return user

    @staticmethod
    async def validate_email(
        email: UserStructure
    ) -> bool:
        """
        Проверка формата email.
        :param user: Информация о пользователе.
        :return: True, если email валиден.
        """
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError('Неверный формат email')
        
        # TODO
        # Нужно добавить проверку, 1 email = 1 юзер.
        # На каждый аккаунт должен быть свой уникальный
        # email

        return True
    
    # soon
    # @staticmethod
    # async def deactivate_user(
    #     user: UserStructure
    # ) -> UserStructure:
    #     """
    #     Деактивация пользователя (установка статуса "Заблокирован").
    #     :param user: Информация о пользователе.
    #     :return: Обновлённый объект пользователя.
    #     """
    #     ...

    @staticmethod
    async def reset_user_password(
        user: UserStructure
    ) -> UserStructure:
        """
        Установка флага на смену пароля при следующем входе.
        :param user: Информация о пользователе.
        :return: Обновлённый объект пользователя.
        """
        ...

class TaskManager:
    TASK_TYPE_LIST = [
        'delete_user',         # Удаление пользователя
        'update_user',         # Обновление данных пользователя
        'create_user',         # Создание нового пользователя
        'reset_password',      # Сброс пароля пользователя
        'block_user',          # Блокировка пользователя
        'unblock_user',        # Разблокировка пользователя

        'add_item',            # Добавление нового товара
        'update_item',         # Обновление информации о товаре
        'delete_item',         # Удаление товара
        'move_item',           # Перемещение товара между складами
        'check_item_stock',    # Проверка наличия товара на складе

        'create_task',         # Создание новой задачи
        'update_task',         # Обновление задачи
        'delete_task',         # Удаление задачи
        'assign_task',         # Назначение задачи пользователю
        'complete_task',       # Пометка задачи как завершенной

        'generate_report',     # Генерация отчета (например, по складу или задачам)
        'export_data',         # Экспорт данных (например, в Excel)
        'import_data',         # Импорт данных в систему

        'update_settings',     # Обновление настроек системы
        'view_logs',           # Просмотр логов действий
        'send_notification',   # Отправка уведомлений пользователям
    ]

    def __init__(self):
        pass

    @property
    def available_task_types(self) -> list[str]:
        """
        Возвращает список доступных типов задач.
        """
        return self.TASK_TYPE_LIST
    
    def check_task_type(self, task_type: str) -> bool:
        """
        Проверяет, является ли тип задачи допустимым.
        """
        if task_type not in self.TASK_TYPE_LIST:
            raise ValueError(f"Недопустимый тип задачи: {task_type}")
        return True
    
    async def create_task(
        self,
        task: str | None = None,
        time: datetime | None = None,
    ):
        ...