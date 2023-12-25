from api_utils.OsuApiUtils import OsuApiUtils
from data_managers import DataUtils
from db_managers import DbManager


class UtilsFactory:
    """
    Utilities factory for all the 'Singleton' type of classes.
    """

    _db_manager: DbManager
    _osu_api_utils: OsuApiUtils

    @classmethod
    async def create_all_instances(cls):
        cls._db_manager = DbManager()
        await cls._db_manager.initialize_tables()
        cls._osu_api_utils = OsuApiUtils(*DataUtils.load_osu_api_credentials())

    @classmethod
    def get_db_manager(cls) -> DbManager:
        return cls._db_manager

    @classmethod
    def get_osu_api_utils(cls) -> OsuApiUtils:
        return cls._osu_api_utils
