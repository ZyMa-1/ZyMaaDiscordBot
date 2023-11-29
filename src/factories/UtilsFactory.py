from api_utils.OsuApiUtils import OsuApiUtils
from data_managers import DataUtils
from db_managers import DbManager


class UtilsFactory:
    """
    Utilities factory for all the 'Singleton' type of classes.
    """
    _db_manager = None
    _osu_api_utils = None

    @classmethod
    async def create_all_instances(cls):
        cls._discord_users_data_db_manager = DbManager()
        await cls._db_manager.create_tables()
        cls._osu_api_utils = OsuApiUtils(*DataUtils.load_osu_api_credentials())

    @classmethod
    def get_db_manager(cls) -> DbManager:
        if not isinstance(cls._db_manager, DbManager):
            raise ValueError
        return cls._db_manager

    @classmethod
    def get_osu_api_utils(cls) -> OsuApiUtils:
        if not isinstance(cls._osu_api_utils, OsuApiUtils):
            raise ValueError
        return cls._osu_api_utils
