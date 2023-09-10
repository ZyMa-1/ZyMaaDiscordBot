import pathlib


class PathManager:
    PROJECT_ROOT: pathlib.Path | None
    TRUSTED_USERS_PATH: pathlib.Path | None
    ADMIN_USERS_PATH: pathlib.Path | None
    DISCORD_USERS_DATA_DB_PATH: pathlib.Path | None

    @classmethod
    def set_project_root(cls, project_root: pathlib.Path):
        cls.PROJECT_ROOT = project_root
        cls.TRUSTED_USERS_PATH = cls.PROJECT_ROOT / "data" / "trusted_users.json"
        cls.ADMIN_USERS_PATH = cls.PROJECT_ROOT / "data" / "admins.json"
        cls.DISCORD_USERS_DATA_DB_PATH = cls.PROJECT_ROOT / "data" / "discord_users_data.db"
