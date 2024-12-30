import asyncio
from datetime import datetime
from src.db import DataBase, DepotItemsStructure

db = DataBase()

data_json = [
    {
        'depot_id': 1,
        'name': 'Предмет 54',
        'barcode': '1234567890123',
        'weight': 1.2,
        'quantity': 10,
        'description': 'Описание предмета 1',
        'status': 'Новый',
        'price': 100.0,
        'depot_section': 12,
        'expiration_date': None,
        'storage_conditions': 'Без особенностей хранения',
        'supplier_id': 1,
        'item_type': 1,
        'image_url': 'http://example.com/item1.jpg',
        'received_at': datetime.utcnow(),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'depot_id': 1,
        'name': 'Предмет 55',
        'barcode': '9876543210987',
        'weight': 2.5,
        'quantity': 20,
        'description': 'Описание предмета 2',
        'status': 'Использованный',
        'price': 50.0,
        'depot_section': 11,
        'expiration_date': None,
        'storage_conditions': 'Без особенностей хранения',
        'supplier_id': 1,
        'item_type': 1,
        'image_url': 'http://example.com/item2.jpg',
        'received_at': datetime.utcnow(),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]

async def main():
    # Инициализация базы данных (если требуется)
    await db.init_db()
    
    for data in data_json:
        data_new = DepotItemsStructure(
            depot_id=data['depot_id'],
            name=data['name'],
            barcode=data['barcode'],
            weight=data['weight'],
            quantity=data['quantity'],
            description=data['description'],
            status=data['status'],
            price=data['price'],
            depot_section=data['depot_section'],
            expiration_date=data['expiration_date'],
            storage_conditions=data['storage_conditions'],
            supplier_id=data['supplier_id'],
            item_type=data['item_type'],
            image_url=data['image_url'],
            received_at=data['received_at'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
    
        data = await db.create_depot_item(data_new)
    
        if data:
            print(f'Предмет {data.name} успешно создан!')
        else:
            print('Ошибка при создании.')

    print('Задача завершена')

if __name__ == '__main__':
    asyncio.run(main())
