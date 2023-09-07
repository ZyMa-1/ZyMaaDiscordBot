import json
import os
from typing import Tuple, List

import aiofiles
from dotenv import load_dotenv

from src.PathManager import PathManager

load_dotenv()


def load_credentials() -> Tuple[str, str]:
    client_id = os.getenv("OSU_APIV2_CLIENT_ID")
    client_secret = os.getenv("OSU_APIV2_CLIENT_SECRET")
    with open("temp_check.json", "r") as f:
        f.writelines([client_id, client_secret])
    return client_id, client_secret


async def load_trusted_users() -> List[str]:
    async with aiofiles.open(PathManager.TRUSTED_USERS_PATH, "r") as file:
        data = await file.read()
        config_data = json.loads(data)
        _trusted_users = config_data["trusted_users"]
        return _trusted_users


def load_discord_bot_token() -> str:
    token = os.getenv("DISCORD_BOT_TOKEN")
    return token
