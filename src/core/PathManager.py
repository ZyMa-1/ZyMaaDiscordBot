import pathlib


class PathManagerError(Exception):
    pass


class PathManager:
    """
    Path manager class to store all paths to the files/directories in more convenient way.
    """
    PROJECT_ROOT: pathlib.Path | None
    DATA_DIR: pathlib.Path | None

    TRUSTED_USERS_PATH: pathlib.Path | None
    ADMIN_USERS_PATH: pathlib.Path | None
    DISCORD_USERS_DATA_DB_PATH: pathlib.Path | None
    DOT_ENV_PATH: pathlib.Path | None

    LOGS_DIR: pathlib.Path | None
    OSU_API_LOGS_PATH: pathlib.Path | None

    @classmethod
    def set_project_root(cls, project_root: pathlib.Path):
        """Sets project root and creates path for all the project files/directories"""
        cls.PROJECT_ROOT = project_root
        cls.DATA_DIR = cls.PROJECT_ROOT / "data"

        cls.TRUSTED_USERS_PATH = cls.PROJECT_ROOT / "data" / "trusted_users.json"
        cls.ADMIN_USERS_PATH = cls.PROJECT_ROOT / "data" / "admins.json"
        cls.DISCORD_USERS_DATA_DB_PATH = cls.PROJECT_ROOT / "data" / "bot_data.db"
        cls.DOT_ENV_PATH = cls.PROJECT_ROOT / ".env"

        cls.LOGS_DIR = cls.PROJECT_ROOT / "logs"
        cls.OSU_API_LOGS_PATH = cls.PROJECT_ROOT / "logs" / "osu_api"

    @classmethod
    def check_paths_existence(cls) -> None:
        """
        Check if all required files and directories exist.
        Raises 'PathManagerError' if any path is missing.
        """
        paths_to_check = [
            cls.DATA_DIR,
            cls.TRUSTED_USERS_PATH,
            cls.ADMIN_USERS_PATH,
            cls.DISCORD_USERS_DATA_DB_PATH,
            cls.DOT_ENV_PATH,
            cls.LOGS_DIR,
            cls.OSU_API_LOGS_PATH,
        ]

        # Check if all paths exist
        missing_paths = [path for path in paths_to_check if not path.exists()]

        if missing_paths:
            raise PathManagerError(f"Missing paths: {missing_paths}")
