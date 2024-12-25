from pydantic import BaseModel, Field
from typing import List, Tuple
from datetime import datetime


class UserStructure(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор пользователя')
    login: str = Field(..., description='Логин пользователя')
    name: str = Field(..., description='Имя пользователя')
    surname: str = Field(..., description='Фамилия пользователя')
    email: str = Field(..., description='Электронная почта')
    phone_number: str = Field(..., description='Номер телефона')
    group_id: int = Field(..., description='ID группы (например: Администраторы, Курьеры, Бухгалтеры)')
    city_id: int = Field(..., description='ID города')
    prefix: str = Field(..., description='Префикс для идентификации')
    password_hash: str = Field(..., description='Хеш пароля, сами пароли не храним')
    status: str | None = Field(None, description='Статус пользователя')
    two_factor: bool = Field(False, description='Включена ли двухфакторная аутентификация')
    is_blocked: bool = Field(False, description='Заблокирован ли пользователь')
    requires_password_reset: bool = Field(False, description='Требуется ли смена пароля при следующем входе')
    created_at: datetime = Field(..., description='Дата создания пользователя')


class CityStructure(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор города')
    name: str = Field(..., description='Название города (например: Гудаута)')
    country: str = Field(..., description='Страна, к которой относится город (например: Абхазия)')


class GroupUsersStructure(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор группы пользователей')
    name: str = Field(..., description='Название группы пользователей')
    rules: List[int] = Field(..., description='Список идентификаторов правил, привязанных к группе')


class DepotStructure(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор склада')
    name: str = Field(..., description='Название склада')
    city_id: int = Field(..., description='ID города, в котором расположен склад')
    address: str = Field(..., description='Адрес склада, например: ул. Новинская 12')
    contact_phone_number: int | None = Field(None, description='Контактный номер телефона (без +)')
    contact_email: str | None = Field(None, description='Контактная электронная почта')
    working_hours: str = Field(..., description='JSON с расписанием работы (пример: tests/example_working_hours.json)')
    postal_code: int = Field(..., description='Почтовый индекс склада (например: 620024)')
    capacity: int | None = Field(None, description='Вместимость склада')
    is_active: bool = Field(True, description='Статус активности склада')
    description: str | None = Field(None, description='Дополнительное описание склада')
    coordinates: Tuple[float, float] | None = Field(None, description='Координаты склада (широта, долгота)')
    manager_name: str | None = Field(None, description='Имя управляющего склада')
    last_inventory_date: datetime | None = Field(None, description='Дата последней инвентаризации')
    type_id: int | None = Field(None, description='ID типа склада')
    related_suppliers: List[int] | None = Field(default_factory=list, description='Список ID связанных поставщиков')
    created_at: datetime = Field(default_factory=datetime.utcnow, description='Дата создания записи о складе')
    updated_at: datetime = Field(default_factory=datetime.utcnow, description='Дата последнего обновления записи')


class DepotSectionModel(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор раздела')
    depot_id: int = Field(..., description='Идентификатор склада, к которому привязан раздел')
    section_name: str = Field(..., max_length=100, description='Название раздела')
    cabinet_number: int = Field(..., description='Номер шкафа')
    shelf_number: int = Field(..., description='Номер полки')
    capacity: int | None = Field(None, description='Вместимость полки (в штуках или объем)')
    max_weight: float | None = Field(None, description='Максимальный вес для полки (в кг)')
    temperature_control: bool = Field(False, description='Есть ли температурный контроль')
    humidity_control: bool = Field(False, description='Контроль влажности')
    description: str | None = Field(None, max_length=255, description='Дополнительные примечания')
    created_at: datetime | None = Field(default_factory=datetime.utcnow, description='Время создания записи')

    class Config:
        orm_mode = True


class DepotItemsStructure(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор предмета')
    depot_id: int = Field(..., description='Идентификатор склада, в котором находится предмет')
    name: str = Field(..., max_length=250, description='Название предмета')
    barcode: str | None = Field(None, max_length=50, description='Штрих-код предмета')
    weight: float | None = Field(None, description='Вес предмета')
    quantity: int = Field(0, description='Количество предмета')
    description: str | None = Field(None, max_length=500, description='Дополнительное описание предмета')
    status: str | None = Field(None, max_length=50, description='Состояние предмета')
    price: float | None = Field(None, description='Стоимость предмета')
    depot_section: int | None = Field(None, description='Секция в складе')  # Привел тип к int
    item_type: int | None = Field(None, description='Тип предмета (например, хрупкий, опасный)')
    image_url: str | None = Field(None, description='URL фотографии предмета')
    received_at: datetime | None = Field(None, description='Дата получения предмета')
    created_at: datetime = Field(..., description='Дата и время добавления предмета на склад')
    updated_at: datetime | None = Field(None, description='Дата последнего обновления информации о предмете')


class DepotItemsType(BaseModel):
    id: int | None = Field(None, description='Уникальный идентификатор типа предмета')
    name: str = Field(..., max_length=250, description='Названия типа предмета')