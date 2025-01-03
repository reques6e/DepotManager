import asyncio
import json

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, 
    DateTime, Float, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select

from passlib.context import CryptContext

from datetime import datetime
from typing import List, Tuple

from src.config import config, settings

from api.models import (
    UserStructure, CityStructure, GroupUsersStructure, DepotStructure,
    DepotSectionModel, DepotItemsStructure
)

Base = declarative_base()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


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

    depot = relationship('Depot', backref='items')
    depot_sections = relationship('DepotSection', backref='items')
    depot_items_type = relationship('DepotItemsType', backref='items')
    supplier = relationship('Supplier', backref='depot_items')


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


class DataBase:
    def __init__(self, db_url: str = f'mysql+asyncmy://{config.DATABASE.user}:{config.DATABASE.password}@{config.DATABASE.host}/{config.DATABASE.name}'):
        self.db_url = db_url
        self.engine = create_async_engine(self.db_url, echo=True)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
    
    async def create_tables(self):
        """Создание таблиц в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    def get_session(self) -> AsyncSession:
        """Получение сессии для работы с базой данных"""
        return self.async_session() 
    
    async def init_db(self):
        """Инициализация базы данных (создание таблиц)"""
        await self.create_tables()

    async def get_depot_by_id(self, depot_id: int):
        """Получение склада по id"""
        async with self.get_session() as session:
            stmt = select(Depot).filter(Depot.id == depot_id)
            result = await session.execute(stmt)
            
            return result.scalar_one_or_none()

    async def get_user(self, user_id: int):
        """Получение пользователя по его ID"""
        async with self.get_session() as session:
            stmt = select(User).filter(User.id == user_id)
            result = await session.execute(stmt)

            return result.scalar_one_or_none()
        
    async def create_group_user(self, group_data: GroupUsersStructure):
        """Создание группы пользователей"""
        
        group = GroupUsers(
            name=group_data.name
        )
        group.set_rules(group_data.rules) 
        
        async with self.get_session() as session:
            session.add(group)
            try:
                await session.commit() 
            except IntegrityError:
                await session.rollback() 
                return None  
            
            return group  

    async def create_depot_item(self, data: DepotItemsStructure):
        """Создание DepotItem"""
        
        nw_data = DepotItems(
            depot_id=data.depot_id,
            name=data.name,
            barcode=data.barcode,
            weight=data.weight,
            quantity=data.quantity,
            description=data.description,
            status=data.status,
            price=data.price,
            depot_section=data.depot_section,
            expiration_date=data.expiration_date,
            storage_conditions=data.storage_conditions, 
            supplier_id=data.supplier_id,
            item_type=data.item_type,
            image_url=data.image_url,
            received_at=data.received_at,
            created_at=data.created_at,
            updated_at=data.updated_at
        )
        
        async with self.get_session() as session:
            session.add(nw_data)
            try:
                await session.commit() 
            except IntegrityError as e:
                await session.rollback()  
                print(e)
                return None  
            
            return nw_data  
        
    async def create_depot_section(self, data: DepotSectionModel):
        """Создание DepotSection"""
        
        nw_data = DepotSection(
            depot_id=data.depot_id,
            section_name=data.section_name,
            cabinet_number=data.cabinet_number,
            shelf_number=data.shelf_number,
            capacity=data.capacity,
            max_weight=data.max_weight,
            temperature_control=data.temperature_control,
            humidity_control=data.humidity_control,
            description=data.description
        )
        
        async with self.get_session() as session:
            session.add(nw_data)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()  
                return None  
            
            return nw_data  
        
    async def create_user(self, user_data: UserStructure):
        """Создание пользователя в таблице users"""
        # Хешируем пароль перед сохранением
        # Сделаю шифрование на фронтенде
        # hashed_password = pwd_context.hash(user_data.password_hash)
        
        user = User(
            login=user_data.login,
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            phone_number=user_data.phone_number,
            group_id=user_data.group_id,
            city_id=user_data.city_id,
            prefix=user_data.prefix,
            password_hash=user_data.password_hash, 
            status=user_data.status,
            two_factor=user_data.two_factor,
            is_blocked=user_data.is_blocked,
            requires_password_reset=user_data.requires_password_reset,
            created_at=user_data.created_at
        )
        
        async with self.get_session() as session:
            session.add(user)
            try:
                await session.commit() 
            except IntegrityError:
                await session.rollback()  
                return None  
            
            return user  
        
    async def authenticate_user(self, login: str, password_hash: str):
        """Проверка логина и пароля пользователя"""
        async with self.get_session() as session:
            stmt = select(User).where(User.login == login)
            try:
                result = await session.execute(stmt)
                user = result.scalar_one()  
            except NoResultFound:
                return None 
            
            if password_hash != user.password_hash:
                return False  # Неверный пароль

            return user  