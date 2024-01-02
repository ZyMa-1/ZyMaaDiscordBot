from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

import my_logging.get_loggers
from db_managers.data_classes import DbUserInfo, DbUserPlayedBeatmapInfo
from db_managers.models.models import UserPlayedBeatmapsTable
from .decorators import elapsed_time_logger

logger = my_logging.get_loggers.database_utilities_logger()


class UserPlayedBeatmapsTableManager:
    """
    Class for managing 'user_played_beatmaps' table database operations (async SQLAlchemy).
    """

    def __init__(self, async_engine: AsyncEngine):
        self.async_engine = async_engine
        self.AsyncSession = async_sessionmaker(self.async_engine, expire_on_commit=False)

    @elapsed_time_logger
    async def merge_user_played_beatmap(self, db_user_played_beatmap: DbUserPlayedBeatmapInfo) -> bool:
        try:
            async with self.AsyncSession() as session:
                beatmap = UserPlayedBeatmapsTable.from_dataclass(db_user_played_beatmap)
                await session.merge(beatmap)
                await session.commit()
            return True
        except IntegrityError as e:
            logger.exception(f"IntegrityError: {e}")
            return False

    @elapsed_time_logger
    async def get_all_user_beatmaps(self, user_info: DbUserInfo) -> List[DbUserPlayedBeatmapInfo]:
        async with self.AsyncSession() as session:
            stmt = select(UserPlayedBeatmapsTable).where(
                UserPlayedBeatmapsTable.user_info_id == user_info.discord_user_id,
                UserPlayedBeatmapsTable._mode == str(user_info.osu_game_mode))
            result = await session.execute(stmt)
            beatmaps = result.scalars().all()
            return [DbUserPlayedBeatmapInfo.from_row(beatmap) for beatmap in beatmaps]
