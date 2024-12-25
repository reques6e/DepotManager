import asyncio
from datetime import datetime
from src.db import DataBase, DepotSectionModel

db = DataBase()


data_json = [
    {
        'depot_id': 1,
        'section_name': 'Секция 1',
        'cabinet_number': 101,
        'shelf_number': 1,
        'capacity': 50,
        'max_weight': 100.5,
        'temperature_control': True,
        'humidity_control': False,
        'description': 'Секция для хранения легких товаров',
        'created_at': datetime.utcnow()
    },
    {
        'depot_id': 1,
        'section_name': 'Секция 2',
        'cabinet_number': 102,
        'shelf_number': 2,
        'capacity': 75,
        'max_weight': 150.0,
        'temperature_control': False,
        'humidity_control': True,
        'description': 'Секция для хранения хрупких товаров',
        'created_at': datetime.utcnow()
    },
    {
        'depot_id': 2,
        'section_name': 'Секция 3',
        'cabinet_number': 103,
        'shelf_number': 3,
        'capacity': 60,
        'max_weight': 200.0,
        'temperature_control': False,
        'humidity_control': False,
        'description': 'Секция для хранения тяжелых товаров',
        'created_at': datetime.utcnow()
    },
    {
        'depot_id': 2,
        'section_name': 'Секция 4',
        'cabinet_number': 104,
        'shelf_number': 4,
        'capacity': 100,
        'max_weight': 250.0,
        'temperature_control': True,
        'humidity_control': True,
        'description': 'Секция с полной системой климат-контроля',
        'created_at': datetime.utcnow()
    },
    {
        'depot_id': 3,
        'section_name': 'Секция 5',
        'cabinet_number': 105,
        'shelf_number': 5,
        'capacity': 80,
        'max_weight': 120.0,
        'temperature_control': False,
        'humidity_control': False,
        'description': 'Секция для хранения бытовой техники',
        'created_at': datetime.utcnow()
    }
]

async def main():
    # Инициализируем базу данных
    # await db.init_db()
    
    for data in data_json:
        data_new = DepotSectionModel(
            depot_id=data['depot_id'],
            section_name=data['section_name'],
            cabinet_number=data['cabinet_number'],
            shelf_number=data['shelf_number'],
            capacity=data['capacity'],
            max_weight=data['max_weight'],
            temperature_control=data['temperature_control'],
            humidity_control=data['humidity_control'],
            description=data.get('description')
        )
    
        data = await db.create_depot_section(data_new)
    
        if data:
            print(f'Успешно создан раздел {data.section_name}')
        else:
            print('Ошибка при создании.')

    print('Задача завершена')

if __name__ == '__main__':
    asyncio.run(main())
