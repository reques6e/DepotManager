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
import aiohttp

from config import settings
from api.models import UserStructure
from packaging.version import Version as _versionCompare


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
        
        return True

    @staticmethod
    async def update_phone_number(
        user: UserStructure, 
        phone_number: str
    ) -> UserStructure:
        """
        Обновление номера телефона пользователя.
        :param user: Информация о пользователе.
        :param phone_number: Новый номер телефона.
        :return: Обновлённый объект пользователя.
        """
        ...

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