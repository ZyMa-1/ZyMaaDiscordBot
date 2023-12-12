import my_logging.get_loggers
from core import PathManager

from .table_managers import UsersTableManager, ScoresTableManager

logger = my_logging.get_loggers.database_utilities_logger()


class DbManager:
    """
    Class for managing database operations (aiosqlite).
    """

    def __init__(self, db_name=PathManager.BOT_DATA_DB_PATH):
        self.db_name = db_name
        self.users_table_manager = UsersTableManager(db_name)
        self.scores_table_manager = ScoresTableManager(db_name)

    async def create_tables(self):
        """
        Initializes all tables.
        """
        await self.users_table_manager.create_users_table()
        await self.scores_table_manager.create_scores_table()

        # Temporary method cals to change the table structure
        await self.scores_table_manager._calculate_mods()
        await self.scores_table_manager._change_column_order()
