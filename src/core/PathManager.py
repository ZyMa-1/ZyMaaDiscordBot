import pathlib


class PathManager:
    """
    Path manager class to store all path to the files/directories in more convenient way.
    """
    PROJECT_ROOT: pathlib.Path | None
    DATA_DIR: pathlib.Path | None
    TEMP_DIR: pathlib.Path | None

    TRUSTED_USERS_PATH: pathlib.Path | None
    ADMIN_USERS_PATH: pathlib.Path | None
    DISCORD_USERS_DATA_DB_PATH: pathlib.Path | None
    DOT_ENV_PATH: pathlib.Path | None

    LOGS_DIR: pathlib.Path | None
    OSU_API_MAIN_LOG_PATH: pathlib.Path | None

    @classmethod
    def set_project_root(cls, project_root: pathlib.Path):
        cls.PROJECT_ROOT = project_root
        cls.DATA_DIR = cls.PROJECT_ROOT / "data"
        cls.TEMP_DIR = cls.PROJECT_ROOT / "data" / "temp"

        cls.TRUSTED_USERS_PATH = cls.PROJECT_ROOT / "data" / "trusted_users.json"
        cls.ADMIN_USERS_PATH = cls.PROJECT_ROOT / "data" / "admins.json"
        cls.DISCORD_USERS_DATA_DB_PATH = cls.PROJECT_ROOT / "data" / "discord_users_data.db"
        cls.DOT_ENV_PATH = cls.PROJECT_ROOT / ".env"

        cls.LOGS_DIR = cls.PROJECT_ROOT / "logs"
        cls.OSU_API_MAIN_LOG_PATH = cls.PROJECT_ROOT / "logs" / "osu_api" / "osu_api.log"
