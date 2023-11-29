import my_logging.get_loggers
from core import PathManager

logger = my_logging.get_loggers.database_utilities_logger()


class ScoresTableManager:
    """
    Class for managing database operations on 'scores' table (aiosqlite).
    """

    def __init__(self, db_name=PathManager.DISCORD_USERS_DATA_DB_PATH):
        self.db_name = db_name
