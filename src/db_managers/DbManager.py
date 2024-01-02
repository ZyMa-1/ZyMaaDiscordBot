from sqlalchemy.ext.asyncio import create_async_engine

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

        self.users_table_manager = UsersTableManager(self.async_engine)
        self.scores_table_manager = ScoresTableManager(self.async_engine)
        self.user_played_beatmaps_table_manager = UserPlayedBeatmapsTableManager(self.async_engine)

    async def initialize_tables(self):
        """
        Initializes all tables.
        """
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
