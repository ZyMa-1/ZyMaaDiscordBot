import pathlib
import random


class PathManagerError(Exception):
    """
    Custom exception class for 'PathManager'.
    """
    pass


class PathManager:
    """
    Path manager class to store all paths to the files/directories in a more convenient way.
    """

    PROJECT_ROOT: pathlib.Path
    DATA_DIR: pathlib.Path

    TRUSTED_USERS: pathlib.Path
    ADMIN_USERS: pathlib.Path
    COMMAND_USAGE: pathlib.Path
    ANIME_GIRLS_DIR: pathlib.Path
    BOT_DATA_DB: pathlib.Path
    DOT_ENV: pathlib.Path

    LOGS_DIR: pathlib.Path
    OSU_API_LOGS_DIR: pathlib.Path
    TEMP_DIR: pathlib.Path

    DATA_UTILITIES_LOG: pathlib.Path
    OSU_API_LOG: pathlib.Path
    DATABASE_UTILITIES_LOG: pathlib.Path
    ROOT_LOG: pathlib.Path

    @classmethod
    def set_project_root(cls, project_root: pathlib.Path):
        """
        Sets project root and creates paths for all the project files/directories.
        """
        cls.PROJECT_ROOT = project_root
        cls.DATA_DIR = cls.PROJECT_ROOT / "data"

        cls.TRUSTED_USERS = cls.DATA_DIR / "trusted_users.json"
        cls.ADMIN_USERS = cls.DATA_DIR / "admins.json"
        cls.COMMAND_USAGE = cls.DATA_DIR / "command_usage.json"
        cls.ANIME_GIRLS_DIR = cls.DATA_DIR / "anime_girls"
        cls.BOT_DATA_DB = cls.DATA_DIR / "bot_data.db"
        cls.DOT_ENV = cls.PROJECT_ROOT / ".env"

        cls.LOGS_DIR = cls.PROJECT_ROOT / "logs"
        cls.OSU_API_LOGS_DIR = cls.LOGS_DIR / "osu_api"  # Used only in logging stats

        # For logging config
        cls.DATA_UTILITIES_LOG = cls.LOGS_DIR / "data_utilities" / "data_utilities.log"
        cls.OSU_API_LOG = cls.LOGS_DIR / "osu_api" / "osu_api.log"
        cls.DATABASE_UTILITIES_LOG = cls.LOGS_DIR / "database_utilities" / "database_utilities.log"
        cls.ROOT_LOG = cls.LOGS_DIR / "root" / "root.log"

        cls.TEMP_DIR = cls.DATA_DIR / "temp"

    @classmethod
    def check_paths_existence(cls) -> None:
        """
        Checks if all required files and directories exist.
        Raises 'PathManagerError' if any path is missing.
        """
        paths_to_check = [
            cls.DATA_DIR,
            cls.TRUSTED_USERS,
            cls.ADMIN_USERS,
            cls.COMMAND_USAGE,
            cls.ANIME_GIRLS_DIR,
            cls.BOT_DATA_DB,
            cls.DOT_ENV,
            cls.LOGS_DIR,
            cls.OSU_API_LOGS_DIR,
            cls.TEMP_DIR
        ]

        # Check if all paths exist
        missing_paths = [path for path in paths_to_check if not path.exists()]

        if missing_paths:
            raise PathManagerError(f"Missing paths: {missing_paths}")

    @classmethod
    def random_anime_girl(cls) -> pathlib.Path:
        """
        Returns a random path of a PNG image from the ANIME_GIRLS_DIR.
        """
        anime_girls = (list(cls.ANIME_GIRLS_DIR.glob("*.jpg")) +
                       list(cls.ANIME_GIRLS_DIR.glob("*.png")) +
                       list(cls.ANIME_GIRLS_DIR.glob("*.jpeg")))
        if not anime_girls:
            raise PathManagerError("No images found in ANIME_GIRLS_DIR")
        return random.choice(anime_girls)
