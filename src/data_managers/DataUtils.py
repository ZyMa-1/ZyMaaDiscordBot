import json
import os
from typing import Tuple, List, Optional

import aiofiles

import my_logging.get_loggers
from core import PathManager

logger = my_logging.get_loggers.data_utilities_logger()


class DataUtils:
    """
    Data utilities class to work with files.
    Self-explanatory methods, so no documentation.
    """

    @staticmethod
    def create_files():
        """
        Creates files if they are not exist.
        """
        if not os.path.exists(PathManager.TRUSTED_USERS_PATH):
            trusted_users_data = {'trusted_users': []}
            with open(PathManager.TRUSTED_USERS_PATH, 'w') as file:
                json.dump(trusted_users_data, file)

        if not os.path.exists(PathManager.ADMIN_USERS_PATH):
            admins_data = {'admins': []}
            with open(PathManager.ADMIN_USERS_PATH, 'w') as file:
                json.dump(admins_data, file)

    @staticmethod
    async def load_trusted_users() -> List[int]:
        async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            logger.info(f"load_trusted_users: {config_data['trusted_users']}")
            return config_data["trusted_users"]

    @staticmethod
    async def load_admin_users() -> List[int]:
        async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            return config_data["admins"]

    @staticmethod
    async def load_first_admin_user() -> Optional[int]:
        async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            return config_data["admins"][0] if config_data["admins"] else None

    @staticmethod
    async def add_trusted_user(discord_user_id: int):
        async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            if discord_user_id not in config_data["trusted_users"]:
                config_data["trusted_users"].append(discord_user_id)
        async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "w") as file:
            await file.write(json.dumps(config_data, indent=4))

    @staticmethod
    async def remove_trusted_user(discord_user_id: int):
        async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            if discord_user_id in config_data["trusted_users"]:
                config_data["trusted_users"].remove(discord_user_id)
        async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "w") as file:
            await file.write(json.dumps(config_data, indent=4))

    @staticmethod
    async def add_admin(discord_user_id: int):
        async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            if discord_user_id not in config_data["admins"]:
                config_data["admins"].append(discord_user_id)
        async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "w") as file:
            await file.write(json.dumps(config_data, indent=4))

    @staticmethod
    async def remove_admin(discord_user_id: int):
        async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "r") as file:
            data = await file.read()
            config_data = json.loads(data)
            if discord_user_id in config_data["admins"]:
                config_data["admins"].remove(discord_user_id)
        async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "w") as file:
            await file.write(json.dumps(config_data, indent=4))

    @staticmethod
    def load_discord_bot_token() -> str:
        token = os.getenv("DISCORD_BOT_TOKEN")
        return token

    @staticmethod
    def load_osu_api_credentials() -> Tuple[str, str]:
        client_id = os.getenv("OSU_APIV2_CLIENT_ID")
        client_secret = os.getenv("OSU_APIV2_CLIENT_SECRET")
        return client_id, client_secret
