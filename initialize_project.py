from pathlib import Path

from src.PathManager import PathManager

# Set the project root first
PathManager.set_project_root(Path(__file__).resolve().parent)

from src.api_utils.ApiUtilsFactory import ApiUtilsFactory
from src.data_managers.data_utils import load_credentials
from src.db_managers.discord_users_data_db_manager import DiscordUsersDataDbManager


async def initialize_resources():
    _API_UTILS = ApiUtilsFactory.create_api_instance(*load_credentials())
    _DB_MANAGER = DiscordUsersDataDbManager()
