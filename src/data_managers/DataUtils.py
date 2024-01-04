import json
import os
from os import PathLike
from typing import Tuple, List, Optional, Literal

import aiofiles

import my_logging.get_loggers
from core import PathManager

logger = my_logging.get_loggers.data_utilities_logger()


class DataUtils:
    """
    Data utilities class to work with files.
    """

    @staticmethod
    async def _file_operation(file_path: PathLike[str], operation: Literal['w', 'r'], data: Optional[dict] = None):
        try:
            async with aiofiles.open(file_path, operation) as file:
                if data is not None:
                    await file.write(json.dumps(data, indent=4))
                else:
                    content = await file.read()
                    return json.loads(content) if content else None
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Error during file operation: {str(e)}")

    @staticmethod
    async def _modify_user(file_path: PathLike[str], key: str, discord_user_id: int, add: bool = True):
        config_data = await DataUtils._file_operation(file_path, 'r')
        user_list = config_data.get(key, []) if config_data else []

        if add and discord_user_id not in user_list:
            user_list.append(discord_user_id)
        elif not add and discord_user_id in user_list:
            user_list.remove(discord_user_id)

        await DataUtils._file_operation(file_path, 'w', {key: user_list})

    @staticmethod
    async def _load_users(file_path: PathLike[str], key: str) -> List[int]:
        config_data = await DataUtils._file_operation(file_path, 'r')
        return config_data.get(key, []) if config_data else []

    @staticmethod
    def create_files():
        files_to_create = [
            (PathManager.TRUSTED_USERS, {'trusted_users': []}),
            (PathManager.ADMIN_USERS, {'admins': []})
        ]
        for file_path, default_data in files_to_create:
            if not os.path.exists(file_path):
                DataUtils._file_operation(file_path, 'w', default_data)

    @staticmethod
    async def load_trusted_users() -> List[int]:
        return await DataUtils._load_users(PathManager.TRUSTED_USERS, 'trusted_users')

    @staticmethod
    async def load_admin_users() -> List[int]:
        return await DataUtils._load_users(PathManager.ADMIN_USERS, 'admins')

    @staticmethod
    async def load_first_admin_user() -> Optional[int]:
        if admins := await DataUtils.load_admin_users():
            return admins[0]
        return None

    @staticmethod
    async def add_trusted_user(discord_user_id: int):
        await DataUtils._modify_user(PathManager.TRUSTED_USERS, 'trusted_users', discord_user_id)

    @staticmethod
    async def remove_trusted_user(discord_user_id: int):
        await DataUtils._modify_user(PathManager.TRUSTED_USERS, 'trusted_users', discord_user_id, add=False)

    @staticmethod
    async def add_admin(discord_user_id: int):
        await DataUtils._modify_user(PathManager.ADMIN_USERS, 'admins', discord_user_id)

    @staticmethod
    async def remove_admin(discord_user_id: int):
        await DataUtils._modify_user(PathManager.ADMIN_USERS, 'admins', discord_user_id, add=False)

    @staticmethod
    def load_discord_bot_token() -> str | None:
        return os.getenv("DISCORD_BOT_TOKEN")

    @staticmethod
    def load_osu_api_credentials() -> Tuple[str | None, str | None]:
        return os.getenv("OSU_APIV2_CLIENT_ID"), os.getenv("OSU_APIV2_CLIENT_SECRET")
