from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

import my_logging.get_loggers
from db_managers.data_classes import DbUserInfo
from db_managers.models.models import UserTable

logger = my_logging.get_loggers.database_utilities_logger()


class UsersTableManager:
    """
    Class for managing 'users' table database operations (async SQLAlchemy).
    """

    def __init__(self, async_engine: AsyncEngine, async_session: async_sessionmaker[AsyncSession]):
        self.async_engine = async_engine
        self.AsyncSession = async_session

    async def merge_user_info(self, user_info: DbUserInfo) -> bool:
        async with self.AsyncSession() as session:
            async with session.begin():
                user = UserTable.from_dataclass(user_info)
                await session.merge(user)
                await session.commit()
        return True

    async def get_user_info(self, discord_user_id: int) -> Optional[DbUserInfo]:
        async with self.AsyncSession() as session:
            result = await session.execute(
               select(UserTable).where(UserTable.discord_user_id == discord_user_id)
            )
            user = result.scalar()
            if user:
                return DbUserInfo.from_row(user)
            else:
                return None
