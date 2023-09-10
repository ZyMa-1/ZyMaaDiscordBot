import json
import os
from typing import Tuple, List

import aiofiles

from src.PathManager import PathManager


async def populate_discord_id_list(discord_user_id_list: List[int]) -> List[Tuple[int, str]]:
    """Adds discord username to every list entry."""
    res = []
    for user_id in discord_user_id_list:
        res.append((user_id, 'fuck'))
    return res


async def add_trusted_user(discord_user_id: int):
    async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
        data = await file.read()
        config_data = json.loads(data)
        if discord_user_id not in config_data["trusted_users"]:
            config_data["trusted_users"].append(discord_user_id)
    async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "w") as file:
        await file.write(json.dumps(config_data, indent=4))


async def remove_trusted_user(discord_user_id: int):
    async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
        data = await file.read()
        config_data = json.loads(data)
        if discord_user_id in config_data["trusted_users"]:
            config_data["trusted_users"].remove(discord_user_id)
    async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "w") as file:
        await file.write(json.dumps(config_data, indent=4))


def load_credentials() -> Tuple[str, str]:
    client_id = os.getenv("OSU_APIV2_CLIENT_ID")
    client_secret = os.getenv("OSU_APIV2_CLIENT_SECRET")
    return client_id, client_secret


async def load_trusted_users(populate=False) -> List[Tuple[int, str]] | List[str]:
    """
    Returns tuple of discord_user_id and discord_username.
    Discord_username is not stored and obtained on fly.
    """
    async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
        data = await file.read()
        config_data = json.loads(data)
        _trusted_users = config_data["trusted_users"]
        return await populate_discord_id_list(_trusted_users) if populate else _trusted_users


async def load_admin_users(populate=False) -> List[Tuple[int, str]] | List[str]:
    async with aiofiles.open(PathManager.ADMIN_USERS_PATH, "r") as file:
        data = await file.read()
        config_data = json.loads(data)
        _admin_users = config_data["admins"]
        return await populate_discord_id_list(_admin_users) if populate else _admin_users


def load_discord_bot_token() -> str:
    token = os.getenv("DISCORD_BOT_TOKEN")
    return token
