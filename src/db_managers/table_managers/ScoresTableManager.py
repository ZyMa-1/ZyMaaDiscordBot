import pathlib

import aiosqlite
from typing import Optional, AsyncGenerator

from ossapi import Mod

import my_logging.get_loggers
from db_managers.data_classes import DbScoreInfo, DbUserInfo
from db_managers.table_managers.decorators import elapsed_time_logger

logger = my_logging.get_loggers.database_utilities_logger()


class ScoresTableManager:
    """
    Class for managing 'scores' table database operations (aiosqlite).
    """

    def __init__(self, db_name: pathlib.Path):
        self.db_name = db_name

    async def create_scores_table(self):
        """
        Initializes 'scores' table.
        """
        async with aiosqlite.connect(self.db_name) as db:
            # Enable foreign key constraints (enforcing checks on foreign keys)
            await db.execute('PRAGMA foreign_keys = ON;')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_info_id INTEGER,
                    score_json_data TEXT,
                    mods INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_info_id) REFERENCES users(discord_user_id)
                )
            ''')
            logger.info("create_scores_table: Table created (or initialized)")
            await db.commit()

    @elapsed_time_logger
    async def insert_score(self, score_info: DbScoreInfo) -> bool:
        """
        Inserts entry to the 'scores' table.
        Returns True If operation was successful, False otherwise.
        """
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.cursor()
                await cursor.execute('''
                    INSERT INTO scores (user_info_id, score_json_data, mods, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (score_info.user_info_id,
                      score_info.score_json_data,
                      score_info.mods.value,
                      score_info.timestamp))
                await db.commit()
            return True
        except aiosqlite.IntegrityError as e:
            logger.exception(f"Foreign key violation: {e}")
            return False

    async def delete_all_user_scores(self, user_info: DbUserInfo) -> bool:
        """
        Deletes all user's scores.
        Returns True If operation was successful, False otherwise.
        """
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'DELETE FROM scores WHERE user_info_id = ?',
                (user_info.discord_user_id,))
            await db.commit()
        return True

    @elapsed_time_logger
    async def get_all_user_scores(self, user_info: DbUserInfo, chunk_size: int = 100) \
            -> AsyncGenerator[DbScoreInfo, None]:
        """
        Returns a generator for all the scores associated with a specified user
        wrapped up into 'DbScoreInfo' dataclass.
        """
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT * FROM scores WHERE user_info_id = ? ORDER BY timestamp DESC',
                (user_info.discord_user_id,))
            while True:
                rows = await cursor.fetchmany(chunk_size)
                if not rows:
                    break

                for row in rows:
                    score_info = DbScoreInfo.from_row(row)
                    yield score_info

    async def count_all_user_scores(self, user_info: DbUserInfo) -> int:
        """
        Counts amount of a user's scores in the 'scores' table.
        """
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                'SELECT COUNT(*) FROM scores WHERE user_info_id = ?',
                (user_info.discord_user_id,))
            count = await cursor.fetchone()

        return count[0]

    async def get_user_random_score(self, user_info: DbUserInfo) -> Optional[DbScoreInfo]:
        """
        Returns a random score (DbScoreInfo db row entry) for the specified user.
        """
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                'SELECT * FROM scores WHERE user_info_id = ? ORDER BY RANDOM() LIMIT 1',
                (user_info.discord_user_id,))
            row = await cursor.fetchone()

        if row:
            return DbScoreInfo.from_row(row)

        return None

    async def check_if_user_has_scores(self, user_info: DbUserInfo) -> bool:
        """
        Checks if a user has at least one score in the 'scores' table.
        """
        scores_count = await self.count_all_user_scores(user_info)
        return scores_count > 0

    @elapsed_time_logger
    async def get_mods_filtered_user_scores(self, user_info: DbUserInfo, mods: Mod, chunk_size: int = 100) \
            -> AsyncGenerator[DbScoreInfo, None]:
        """
        Filters the 'scores' table by 'mods' column which include provided mods.
        Returns a generator for all the scores associated with a specified user
        wrapped up into 'DbScoreInfo' dataclass.
        """
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT * FROM scores WHERE user_info_id = ? AND (mods & ?) = ?',
                (user_info.discord_user_id, mods.value, mods.value))
            while True:
                rows = await cursor.fetchmany(chunk_size)
                if not rows:
                    break

                for row in rows:
                    score_info = DbScoreInfo.from_row(row)
                    yield score_info

    async def _calculate_mods(self, chunk_size: int = 100):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                # Add mods INTEGER column with default value NULL
                cursor = await db.cursor()
                await cursor.execute("PRAGMA table_info(scores)")
                columns = [column[1] for column in await cursor.fetchall()]  # Get column names

                if 'mods' not in columns:
                    await cursor.execute('ALTER TABLE scores ADD COLUMN mods INTEGER DEFAULT NULL')

                # Calculate the mods for each row
                cursor = await db.cursor()
                await cursor.execute('SELECT id, score_json_data FROM scores WHERE mods IS NULL')

                while True:
                    rows = await cursor.fetchmany(chunk_size)
                    if not rows:
                        break

                    for row in rows:
                        row_id, score_json_data = row
                        deserialized_json = DbScoreInfo.deserialize_score_json_static(score_json_data)
                        try:
                            mod_value = deserialized_json['mods']
                        except ValueError:
                            logger.exception("Error trying to create 'Mod' instance")

                        await cursor.execute(
                            'UPDATE scores SET mods = ? WHERE id = ?',
                            (mod_value, row_id))

                await db.commit()

        except Exception as e:
            try:
                await db.rollback()
            except Exception as e2:
                logger.exception(f"Cannot rollback. Error during mods calculation: {e2}")
            logger.exception(f"Error during mods calculation: {e}")
