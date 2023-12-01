import pathlib


class PathManagerError(Exception):
    """
    Custom exception class for 'PathManager'.
    """
    pass


class PathManager:
    """
    Path manager class to store all paths to the files/directories in more convenient way.
    """

    PROJECT_ROOT: pathlib.Path
    DATA_DIR: pathlib.Path

    TRUSTED_USERS_PATH: pathlib.Path
    ADMIN_USERS_PATH: pathlib.Path
    BOT_DATA_DB_PATH: pathlib.Path
    DOT_ENV_PATH: pathlib.Path

    LOGS_DIR: pathlib.Path
    OSU_API_LOGS_PATH: pathlib.Path
    TEMP_DIR: pathlib.Path

    @classmethod
    def set_project_root(cls, project_root: pathlib.Path):
        """
        Sets project root and creates path for all the project files/directories.
        """
        cls.PROJECT_ROOT = project_root
        cls.DATA_DIR = cls.PROJECT_ROOT / "data"

        cls.TRUSTED_USERS_PATH = cls.PROJECT_ROOT / "data" / "trusted_users.json"
        cls.ADMIN_USERS_PATH = cls.PROJECT_ROOT / "data" / "admins.json"
        cls.BOT_DATA_DB_PATH = cls.PROJECT_ROOT / "data" / "bot_data.db"
        cls.DOT_ENV_PATH = cls.PROJECT_ROOT / ".env"

        cls.LOGS_DIR = cls.PROJECT_ROOT / "logs"
        cls.OSU_API_LOGS_PATH = cls.PROJECT_ROOT / "logs" / "osu_api"
        cls.TEMP_DIR = cls.PROJECT_ROOT / "data" / "temp"

    @classmethod
    def check_paths_existence(cls) -> None:
        """
        Checks if all required files and directories exist.
        Raises 'PathManagerError' if any path is missing.
        """
        paths_to_check = [
            cls.DATA_DIR,
            cls.TRUSTED_USERS_PATH,
            cls.ADMIN_USERS_PATH,
            cls.BOT_DATA_DB_PATH,
            cls.DOT_ENV_PATH,
            cls.LOGS_DIR,
            cls.OSU_API_LOGS_PATH,
            cls.TEMP_DIR
        ]

        # Check if all paths exist
        missing_paths = [path for path in paths_to_check if not path.exists()]

        if missing_paths:
            raise PathManagerError(f"Missing paths: {missing_paths}")
