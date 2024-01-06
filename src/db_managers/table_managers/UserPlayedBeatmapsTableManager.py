from typing import List, Optional

from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession

import my_logging.get_loggers
from db_managers.data_classes import DbUserInfo, DbUserPlayedBeatmapInfo
from db_managers.models.models import UserPlayedBeatmapsTable
from .decorators import elapsed_time_logger

logger = my_logging.get_loggers.database_utilities_logger()


class UserPlayedBeatmapsTableManager:
    """
    Class for managing 'user_played_beatmaps' table database operations (async SQLAlchemy).
    """

    def __init__(self, async_engine: AsyncEngine, async_session: async_sessionmaker[AsyncSession]):
        self.async_engine = async_engine
        self.AsyncSession = async_session

    @elapsed_time_logger
    async def merge_user_beatmap(self, db_user_played_beatmap: DbUserPlayedBeatmapInfo) -> bool:
        try:
            async with self.AsyncSession() as session:
                beatmap = UserPlayedBeatmapsTable.from_dataclass(db_user_played_beatmap)
                await session.merge(beatmap)
                await session.commit()
            return True
        except IntegrityError as e:
            logger.exception(f"IntegrityError: {e}")
            return False

    async def delete_all_user_beatmaps(self, user_info: DbUserInfo) -> bool:
        async with self.AsyncSession() as session:
            await session.execute(
                delete(UserPlayedBeatmapsTable).where(
                    UserPlayedBeatmapsTable.user_info_id == user_info.discord_user_id,
                    UserPlayedBeatmapsTable._mode == str(user_info.osu_game_mode))
            )
            await session.commit()
        return True

    async def count_all_user_beatmaps(self, user_info: DbUserInfo) -> int:
        async with self.AsyncSession() as session:
            stmt = select(func.count()).where(
                UserPlayedBeatmapsTable.user_info_id == user_info.discord_user_id,
                UserPlayedBeatmapsTable._mode == str(user_info.osu_game_mode))
            count = await session.execute(stmt)
        return count.scalar()

    async def get_user_random_beatmap(self, user_info: DbUserInfo) -> Optional[DbUserPlayedBeatmapInfo]:
        async with self.AsyncSession() as session:
            stmt = select(UserPlayedBeatmapsTable).where(
                UserPlayedBeatmapsTable.user_info_id == user_info.discord_user_id,
                UserPlayedBeatmapsTable._mode == str(user_info.osu_game_mode)
            ).order_by(
                func.random()).limit(1)
            row = await session.execute(stmt)
            beatmap = row.scalar()

        if beatmap:
            return DbUserPlayedBeatmapInfo.from_row(beatmap)

        return None

    async def check_if_user_has_beatmaps(self, user_info: DbUserInfo) -> bool:
        beatmaps_count = await self.count_all_user_beatmaps(user_info)
        return beatmaps_count > 0

    @elapsed_time_logger
    async def get_all_user_beatmaps(self, user_info: DbUserInfo) -> List[DbUserPlayedBeatmapInfo]:
        async with self.AsyncSession() as session:
            stmt = select(UserPlayedBeatmapsTable).where(
                UserPlayedBeatmapsTable.user_info_id == user_info.discord_user_id,
                UserPlayedBeatmapsTable._mode == str(user_info.osu_game_mode))
            result = await session.execute(stmt)
            beatmaps = result.scalars().all()
            return [DbUserPlayedBeatmapInfo.from_row(beatmap) for beatmap in beatmaps]
