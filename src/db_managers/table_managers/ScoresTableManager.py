from typing import List

from ossapi import Mod
from sqlalchemy import delete, select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

import my_logging.get_loggers
from db_managers.data_classes import DbScoreInfo, DbUserInfo
from db_managers.models.models import ScoreTable
from db_managers.table_managers.decorators import elapsed_time_logger

logger = my_logging.get_loggers.database_utilities_logger()


class ScoresTableManager:
    """
    Class for managing 'scores' table database operations (async SQLAlchemy).
    """

    def __init__(self, async_engine: AsyncEngine):
        self.async_engine = async_engine
        self.AsyncSession = async_sessionmaker(self.async_engine, expire_on_commit=False)

    @elapsed_time_logger
    async def insert_score(self, score_info: DbScoreInfo) -> bool:
        """
        Inserts entry to the 'scores' table.
        Returns True If operation was successful, False otherwise.
        """
        try:
            async with self.AsyncSession() as session:
                score = ScoreTable.from_db_score_info(score_info)
                await session.merge(score)
                await session.commit()
            return True
        except IntegrityError as e:
            logger.exception(f"Foreign key violation: {e}")
            return False

    async def delete_all_user_scores(self, user_info: DbUserInfo) -> bool:
        """
        Deletes all user's scores.
        Returns True If operation was successful, False otherwise.
        """
        async with self.AsyncSession() as session:
            await session.execute(
                delete(ScoreTable).where(ScoreTable.user_info_id == user_info.discord_user_id)
            )
            await session.commit()
        return True

    @elapsed_time_logger
    async def get_all_user_scores(self, user_info: DbUserInfo) -> List[DbScoreInfo]:
        """
        Returns a generator for all the scores associated with a specified user
        wrapped up into 'DbScoreInfo' dataclass.
        """
        async with self.AsyncSession() as session:
            stmt = select(ScoreTable).where(ScoreTable.user_info_id == user_info.discord_user_id).order_by(
                ScoreTable.timestamp.desc()
            )
            result = await session.execute(stmt)
            scores = result.scalars().all()
            return [DbScoreInfo.from_row(score) for score in scores]

    async def count_all_user_scores(self, user_info: DbUserInfo) -> int:
        """
        Counts amount of a user's scores in the 'scores' table.
        """
        async with self.AsyncSession() as session:
            stmt = select(func.count()).where(ScoreTable.user_info_id == user_info.discord_user_id)
            count = await session.execute(stmt)
        return count.scalar()

    async def get_user_random_score(self, user_info: DbUserInfo):
        """
        Returns a random score (DbScoreInfo db row entry) for the specified user.
        """
        async with self.AsyncSession() as session:
            stmt = select(ScoreTable).where(ScoreTable.user_info_id == user_info.discord_user_id).order_by(
                func.random()).limit(1)
            row = await session.execute(stmt)
            score = row.scalar()

        if score:
            return DbScoreInfo.from_row(score)

        return None

    async def check_if_user_has_scores(self, user_info: DbUserInfo) -> bool:
        """
        Checks if a user has at least one score in the 'scores' table.
        """
        scores_count = await self.count_all_user_scores(user_info)
        return scores_count > 0

    @elapsed_time_logger
    async def get_mods_filtered_user_scores(self, user_info: DbUserInfo, mods: Mod) -> List[DbScoreInfo]:
        """
        Filters the 'scores' table by 'mods' column which include provided mods.
        Returns a generator for all the scores associated with a specified user
        wrapped up into 'DbScoreInfo' dataclass.
        """
        async with self.AsyncSession() as session:
            stmt = select(ScoreTable).where(
                and_(
                    ScoreTable.user_info_id == user_info.discord_user_id,
                    (ScoreTable._mods.op('&')(mods.value) == mods.value)
                )
            )
            result = await session.execute(stmt)
            scores = result.scalars().all()
            return [DbScoreInfo.from_row(score) for score in scores]
