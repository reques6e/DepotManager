import asyncio
from datetime import datetime
from src.db import DataBase, GroupUsersStructure

db = DataBase()


data_json = [
    {
        'name': 'Управляющий',
        'rules': [777]
    },
    {
        'name': 'Складской работник',
        'rules': [778]
    },
    {
        'name': 'Инвентаризатор',
        'rules': [779]
    },
    {
        'name': 'Кладовщик',
        'rules': [780]
    },
    {
        'name': 'Охрана',
        'rules': [781]
    },
    {
        'name': 'Администратор системы',
        'rules': [782]
    },
    {
        'name': 'Товаровед',
        'rules': [783]
    },
    {
        'name': 'Рабочий на складе (грузчик)',
        'rules': [784]
    },
    {
        'name': 'Менеджер по складу',
        'rules': [785]
    },
    {
        'name': 'Экспедитор',
        'rules': [786]
    },
    {
        'name': 'Техник склада',
        'rules': [787]
    },
    {
        'name': 'Механик',
        'rules': [788]
    },
    {
        'name': 'Координатор логистики',
        'rules': [789]
    },
    {
        'name': 'Аналитик склада',
        'rules': [790]
    },
    {
        'name': 'Ответственный за технику безопасности',
        'rules': [791]
    },
    {
        'name': 'Контролёр качества',
        'rules': [792]
    },
]


async def main():
    # Инициализируем базу данных
    # await db.init_db()
    
    for data in data_json:
        data_new = GroupUsersStructure(
            name=data['name'],
            rules=data['rules']
        )
    
        data = await db.create_group_user(data_new)
    
        if data:
            print(f'Группа {data.name} успешно создана!')
        else:
            print('Ошибка при создании.')

    print('Задача завершена')

if __name__ == '__main__':
    asyncio.run(main())
