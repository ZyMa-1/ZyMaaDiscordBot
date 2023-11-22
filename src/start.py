import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

import bot
import my_logging.get_loggers
import my_logging.setup_logging
from core import PathManager


def create_directories():
    os.makedirs(PathManager.DATA_DIR, exist_ok=True)
    os.makedirs(PathManager.TEMP_DIR, exist_ok=True)  # not used for now


async def main():
    # Set the project root first
    PathManager.set_project_root(Path(__file__).resolve().parent.parent)
    os.chdir(PathManager.PROJECT_ROOT)

    # Create directories if there are not there
    create_directories()

    # Load environment variables
    load_dotenv(dotenv_path=PathManager.DOT_ENV_PATH)

    # Setting up my_logging
    my_logging.setup_logging.main()

    # Creating all resources
    from factories import UtilsFactory
    await UtilsFactory.create_all_instances()

    # Starting  the bot
    await bot.main()


if __name__ == "__main__":
    asyncio.run(main())
