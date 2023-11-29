import aiosqlite

import my_logging.get_loggers
from core import PathManager
from db_managers.data_classes import DbUserInfo

logger = my_logging.get_loggers.database_utilities_logger()


class UsersTableManager:
    """
    Class for managing 'users' table database operations (aiosqlite).
    """

    def __init__(self, db_name=PathManager.DISCORD_USERS_DATA_DB_PATH):
        self.db_name = db_name

    async def create_users_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    discord_user_id INTEGER PRIMARY KEY,
                    osu_user_id INTEGER,
                    osu_game_mode TEXT
                )
            ''')
            logger.info("create_users_table: Table created (or initialized)")
            await db.commit()

    async def insert_user_info(self, user_info: DbUserInfo) -> bool:
        if not user_info.is_config_set_up() or not user_info.are_fields_valid():
            return False

        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'INSERT OR REPLACE INTO users (discord_user_id, osu_user_id, osu_game_mode) VALUES (?, ?, ?)',
                user_info.as_tuple())
            await db.commit()

            return True

    async def get_user_info(self, discord_user_id: int) -> DbUserInfo:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT osu_user_id, osu_game_mode FROM users WHERE discord_user_id = ?',
                                 (discord_user_id,))
            result = await cursor.fetchone()
            if result:
                osu_user_id, osu_game_mode = result
                return DbUserInfo(discord_user_id, osu_user_id, osu_game_mode)
            else:
                return DbUserInfo(discord_user_id, None, None)
