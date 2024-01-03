from typing import TYPE_CHECKING

from data_managers import DataUtils

if TYPE_CHECKING:
    from api_utils.OsuApiUtils import OsuApiUtils
    from db_managers import DbManager


class UtilsFactory:
    """
    Utilities factory for all the 'Singleton' type of classes.
    """

    _db_manager: 'DbManager' = None
    _osu_api_utils: 'OsuApiUtils' = None

    @classmethod
    async def create_all_instances(cls):
        from api_utils.OsuApiUtils import OsuApiUtils
        cls._osu_api_utils = OsuApiUtils(*DataUtils.load_osu_api_credentials())
        from db_managers import DbManager
        cls._db_manager = DbManager()
        await cls._db_manager.initialize_tables()

    @classmethod
    def get_db_manager(cls) -> 'DbManager':
        return cls._db_manager

    @classmethod
    def get_osu_api_utils(cls) -> 'OsuApiUtils':
        return cls._osu_api_utils
