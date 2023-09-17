from pathlib import Path

from dotenv import load_dotenv

from src.PathManager import PathManager

# Set the project root first
PathManager.set_project_root(Path(__file__).resolve().parent)

# Load environment variables
load_dotenv()

from src.api_utils.ApiUtils import ApiUtils
from src.data_managers.DataUtils import DataUtils
from src.db_managers.DiscordUsersDataDbManager import DiscordUsersDataDbManager


# Initialize classes that have some authorization logic in the __init__
async def initialize_resources():
    _API_UTILS = ApiUtils(*DataUtils.load_credentials())
    _DB_MANAGER = DiscordUsersDataDbManager()
