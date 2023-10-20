from api_utils.OsuApiUtils import OsuApiUtils
from data_managers import DataUtils
from db_managers import DiscordUsersDataDbManager


class UtilsFactory:
    _discord_users_data_db_manager = None
    _osu_api_utils = None

    @classmethod
    async def create_all_instances(cls):
        cls._discord_users_data_db_manager = DiscordUsersDataDbManager()
        await cls._discord_users_data_db_manager.create_users_table()
        cls._osu_api_utils = OsuApiUtils(*DataUtils.load_osu_api_credentials())

    @classmethod
    def get_discord_users_data_db_manager(cls):
        if not isinstance(cls._discord_users_data_db_manager, DiscordUsersDataDbManager):
            raise ValueError
        return cls._discord_users_data_db_manager

    @classmethod
    def get_osu_api_utils(cls):
        if not isinstance(cls._osu_api_utils, OsuApiUtils):
            raise ValueError
        return cls._osu_api_utils
