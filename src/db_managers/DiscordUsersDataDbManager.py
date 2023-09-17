from typing import Tuple

import aiosqlite

from src.PathManager import PathManager
from src.external_stuff import SingletonMeta


class DiscordUsersDataDbManager(metaclass=SingletonMeta):
    def __init__(self, db_name=PathManager.DISCORD_USERS_DATA_DB_PATH):
        self.db_name = db_name

    async def create_users_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    discord_username TEXT PRIMARY KEY,
                    osu_user_id INTEGER,
                    osu_game_mode TEXT
                )
            ''')
            await db.commit()

    async def insert_user_info(self, discord_username: str, osu_user_id: int, osu_game_mode: str):
        print('insert', discord_username, osu_user_id, osu_game_mode)
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'INSERT OR REPLACE INTO users (discord_username, osu_user_id, osu_game_mode) VALUES (?, ?, ?)',
                (discord_username, osu_user_id, osu_game_mode))
            await db.commit()

    async def get_user_info(self, discord_username: str) -> Tuple[int, str] | Tuple[None, None]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT osu_user_id, osu_game_mode FROM users WHERE discord_username = ?',
                                 (discord_username,))
            result = await cursor.fetchone()
            if result:
                osu_user_id, osu_game_mode = result
                return osu_user_id, osu_game_mode
            else:
                return None, None
