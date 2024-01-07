from typing import List, Optional

from ossapi import Mod
from sqlalchemy import delete, select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession

import my_logging.get_loggers
from db_managers.data_classes import DbScoreInfo, DbUserInfo
from db_managers.models.models import ScoreTable
from .decorators import elapsed_time_logger

logger = my_logging.get_loggers.database_utilities_logger()


class ScoresTableManager:
    """
    Class for managing 'scores' table database operations (async SQLAlchemy).
    """

    def __init__(self, async_engine: AsyncEngine, async_session: async_sessionmaker[AsyncSession]):
        self.async_engine = async_engine
        self.AsyncSession = async_session

    async def merge_score_info(self, score_info: DbScoreInfo) -> bool:
        try:
            async with self.AsyncSession() as session:
                score = ScoreTable.from_dataclass(score_info)
                await session.merge(score)
                await session.commit()
            return True
        except IntegrityError:
            logger.exception(f"IntegrityError: {__name__}")
            return False

    async def delete_all_user_scores(self, user_info: DbUserInfo) -> bool:
        try:
            async with self.AsyncSession() as session:
                await session.execute(
                    delete(ScoreTable).where(
                        ScoreTable.user_info_id == user_info.discord_user_id,
                        ScoreTable._mode == user_info._osu_game_mode)
                )
                await session.commit()
            return True
        except Exception as e:
            logger.exception(f"Exception db: {e}")
            return False

    @elapsed_time_logger
    async def get_all_user_scores(self, user_info: DbUserInfo) -> List[DbScoreInfo]:
        async with self.AsyncSession() as session:
            stmt = select(ScoreTable).where(
                ScoreTable.user_info_id == user_info.discord_user_id,
                ScoreTable._mode == user_info._osu_game_mode
            ).order_by(
                ScoreTable.timestamp.desc()
            )
            result = await session.execute(stmt)
            scores = result.scalars().all()
            return [DbScoreInfo.from_row(score) for score in scores]

    async def count_all_user_scores(self, user_info: DbUserInfo) -> int:
        async with self.AsyncSession() as session:
            stmt = select(func.count()).where(
                ScoreTable.user_info_id == user_info.discord_user_id,
                ScoreTable._mode == user_info._osu_game_mode)
            count = await session.execute(stmt)
        return count.scalar() or 0

    async def get_user_random_score(self, user_info: DbUserInfo) -> Optional[DbScoreInfo]:
        async with self.AsyncSession() as session:
            stmt = select(ScoreTable).where(
                ScoreTable.user_info_id == user_info.discord_user_id,
                ScoreTable._mode == user_info._osu_game_mode
            ).order_by(
                func.random()).limit(1)
            row = await session.execute(stmt)
            score = row.scalar()
        if score:
            return DbScoreInfo.from_row(score)
        return None

    async def check_if_user_has_scores(self, user_info: DbUserInfo) -> bool:
        scores_count = await self.count_all_user_scores(user_info)
        return scores_count > 0

    @elapsed_time_logger
    async def get_mods_filtered_user_scores(self, user_info: DbUserInfo, mods: Mod) -> List[DbScoreInfo]:
        async with self.AsyncSession() as session:
            stmt = select(ScoreTable).where(
                and_(
                    ScoreTable.user_info_id == user_info.discord_user_id,
                    (ScoreTable._mods.op('&')(mods.value) == mods.value),
                    ScoreTable._mode == user_info._osu_game_mode
                )
            )
            result = await session.execute(stmt)
            scores = result.scalars().all()
            return [DbScoreInfo.from_row(score) for score in scores]
