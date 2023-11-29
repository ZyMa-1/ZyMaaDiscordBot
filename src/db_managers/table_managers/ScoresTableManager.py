import aiosqlite
from typing import List, Generator

import my_logging.get_loggers
from core import PathManager
from db_managers.data_classes import DbScoreInfo

logger = my_logging.get_loggers.database_utilities_logger()


class ScoresTableManager:
    """
    Class for managing 'scores' table database operations (aiosqlite).
    """

    def __init__(self, db_name=PathManager.DISCORD_USERS_DATA_DB_PATH):
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
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_info_id) REFERENCES users(discord_user_id)
                )
            ''')
            logger.info("create_scores_table: Table created (or initialized)")
            await db.commit()

    async def insert_score(self, score_info: DbScoreInfo) -> bool:
        """
        Inserts entry to 'scores' table.
        Returns True If operation was successful, False otherwise.
        """
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.cursor()
                await cursor.execute('''
                    INSERT INTO scores (user_info_id, score_json_data, timestamp)
                    VALUES (?, ?, ?)
                ''', (score_info.user_info_id, score_info.score_json_data, score_info.timestamp))
                await db.commit()
            return True
        except aiosqlite.IntegrityError as e:
            logger.exception(f"Foreign key violation: {e}")
            return False

    async def delete_score(self, _id: int) -> bool:
        """
        Inserts entry to 'scores' table.
        Returns True If operation was successful, False otherwise.
        """
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.cursor()
                await cursor.execute('DELETE FROM scores WHERE id = ?', (_id,))
                await db.commit()
            return True
        except aiosqlite.Error:
            return False

    async def get_all_user_scores(self, user_info_id: int) -> Generator[DbScoreInfo, None, None]:
        """
        Returns a generator for all the scores associated with a specified user
        wrapped up into 'DbScoreInfo' dataclass.
        """
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.execute('''
                SELECT id, user_info_id, score_json_data, timestamp
                FROM scores
                WHERE user_info_id = ?
                ORDER BY timestamp DESC
            ''', (user_info_id,))
            rows = await cursor.fetchall()
            for row in rows:
                db_score_info = DbScoreInfo(id=row[0],
                                            user_info_id=row[1],
                                            score_json_data=row[2],
                                            timestamp=row[3])
                yield db_score_info
