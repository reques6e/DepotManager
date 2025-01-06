from sqlalchemy import select, and_
from sqlalchemy.exc import NoResultFound

from dao.base import BaseDAO
from src.db import GroupUsers, async_session_maker
from api.models import GroupUsersStructure


class GroupDAO(BaseDAO):
    model = GroupUsers

    @classmethod
    async def get_all():
        """
        Получает все группы
        """
        query = select(GroupUsers.id, GroupUsers.name, GroupUsers.rules)
        async with async_session_maker() as session:
            result = await session.execute(query)
            return [
                {
                    'id': row.id, 
                    'name': row.name, 
                    'rules': row.rules
                } 
                for row in result.fetchall()
            ]
            
    @classmethod
    async def delete_group(group_id: int) -> bool:
        """
        Удаление группы
        """
        query = select(GroupUsers).filter(GroupUsers.id == group_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            group = result.scalar_one_or_none()

            if not group:
                return None 

            await session.delete(group)
            try:
                await session.commit()  
                return True
            except:
                await session.rollback() 
                return False

    @classmethod
    async def update_group(group_data: GroupUsersStructure) -> GroupUsers | None:
        """
        Обновление данных группы
        """
        query = select(GroupUsers).filter(GroupUsers.id == group_data.id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            group = result.scalar_one_or_none()

            if not group:
                return None 

            group.name = group_data.name
            group.set_rules(group_data.rules)

            try:
                await session.commit() 
                return group
            except:
                await session.rollback()  
                return False