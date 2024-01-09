from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import my_logging.get_loggers
from core import PathManager
from .models.base import Base
from .table_managers import UsersTableManager, ScoresTableManager, UserPlayedBeatmapsTableManager

logger = my_logging.get_loggers.database_utilities_logger()


class DbManager:
    """
    Class for managing database operations (async SQLAlchemy).
    """

    def __init__(self, db_name=PathManager.BOT_DATA_DB):
        self.db_name = db_name
        self.async_engine = create_async_engine(f'sqlite+aiosqlite:///{db_name}', echo=False)
        self.async_session = async_sessionmaker(self.async_engine, expire_on_commit=False)

        self.users: UsersTableManager = UsersTableManager(self.async_engine, self.async_session)
        self.scores: ScoresTableManager = ScoresTableManager(self.async_engine, self.async_session)
        self.user_played_beatmaps: UserPlayedBeatmapsTableManager = UserPlayedBeatmapsTableManager(self.async_engine,
                                                                                                   self.async_session)

    async def initialize_tables(self):
        """
        Initializes all tables.
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
