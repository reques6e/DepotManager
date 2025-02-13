import asyncio
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship

from sqlalchemy import Column, Integer, String
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, 
    DateTime, Float, ForeignKey
)
from config import settings

# Настройка подключения к базе данных
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Таблицы
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    group_id = Column(Integer, nullable=False)
    city_id = Column(Integer, nullable=False)
    prefix = Column(String(10), nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(50), nullable=True)
    two_factor = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    requires_password_reset = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)


class GroupUsers(Base):
    __tablename__ = 'group_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    rules = Column(String(255))  # Храним JSON как строку

    def set_rules(self, rules: list[int]):
        """Преобразуем список правил в строку JSON"""
        self.rules = json.dumps(rules)

    def get_rules(self) -> list[int]:
        """Преобразуем строку JSON обратно в список правил"""
        return json.loads(self.rules) if self.rules else []

class Depot(Base):
    __tablename__ = 'depots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    address = Column(String(255), nullable=False)
    contact_phone_number = Column(Integer, nullable=True)
    contact_email = Column(String(255), nullable=True)
    working_hours = Column(String(255), nullable=False)  # JSON как строка
    postal_code = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
    coordinates = Column(String(255), nullable=True)  # Широта, долгота в строке
    manager_name = Column(String(255), nullable=True)
    last_inventory_date = Column(DateTime, nullable=True)
    type_id = Column(Integer, nullable=True)
    related_suppliers = Column(String(255), nullable=True)  # Список ID через запятую
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    city = relationship('City', backref='depots')  # Связь с городами


class DepotSection(Base):
    __tablename__ = 'depot_sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    depot_id = Column(Integer, ForeignKey('depots.id'), nullable=False)
    section_name = Column(String(100), nullable=False)
    cabinet_number = Column(Integer, nullable=False)
    shelf_number = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=True)
    max_weight = Column(Float, nullable=True)
    temperature_control = Column(Boolean, default=False)
    humidity_control = Column(Boolean, default=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    depot = relationship('Depot', backref='sections')  # Связь с таблицей складов


class DepotItems(Base):
    __tablename__ = 'depot_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    depot_id = Column(Integer, ForeignKey('depots.id'), nullable=False)
    name = Column(String(250), nullable=False)
    barcode = Column(String(50), nullable=True)
    weight = Column(Float, nullable=True)
    quantity = Column(Integer, default=0)
    description = Column(String(500), nullable=True)
    status = Column(String(50), nullable=True)
    price = Column(Float, nullable=True)
    depot_section = Column(Integer, ForeignKey('depot_sections.id'), nullable=True)
    expiration_date = Column(Integer, nullable=True)
    storage_conditions = Column(String(255), nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)  # Добавлен ForeignKey на таблицу поставщиков
    item_type = Column(Integer, ForeignKey('depot_items_type.id'), nullable=True)
    image_url = Column(String(255), nullable=True)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    depot = relationship('Depot', backref='items') # Связь с таблицей складов
    depot_sections = relationship('DepotSection', backref='items') # Связь с таблицей секции складов
    depot_items_type = relationship('DepotItemsType', backref='items') # Связь с таблицей типов items складов
    supplier = relationship('Supplier', backref='depot_items') # Связь с таблицей поставщиков


class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=False)
    contact_email = Column(String(100), nullable=True)
    address = Column(String(300), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=False)
    registration_number = Column(String(50), nullable=True)
    tax_identification_number = Column(String(50), nullable=True)
    payment_terms = Column(String(200), nullable=True)
    bank_details = Column(String(255), nullable=True)
    average_delivery_time = Column(Integer, nullable=True)
    reliability_rating = Column(Float, nullable=True)
    compliance_certificates = Column(String(255), nullable=True)
    preferred = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DepotItemsType(Base):
    __tablename__ = 'depot_items_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)

class DepotCompanyCars(Base):
    __tablename__ = 'company_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False) # Название машины (НЕ МОДЕЛЬ!)
    brand = Column(String(100), nullable=False) # Бренд (Toyota, BMW, ... )
    model = Column(String(100), nullable=False) # Название модели
    vin_body_number = Column(String(17), nullable=False) # ВИН или номер кузова (для японских авто)
    year = Column(Integer, nullable=False) # Год выпуска авто
    license_plates = Column(String(100), nullable=True) # Гос. номера авто
    vehicle_payload = Column(Integer, nullable=False) # Грузоподъемность авто (в кг)
    fuel_type = Column(String(100), nullable=True) # Тип топлива (бензин, дизель, электро)


class Attachment(Base):
    __tablename__ = 'attachment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(100), nullable=False) # UUID вложения
    file_path = Column(String(250), nullable=False) # Путь к файлу (это не URL)
    attachment_type = Column(String(100), nullable=False) # Тип вложения: видео, фото, файл
    file_extension = Column(String(100), nullable=False) # Расширение файла

async def create_tables():
    async with engine.begin() as conn:
        print('Создание таблицы')
        await conn.run_sync(Base.metadata.create_all)
        print('Таблица была успешно создана')
