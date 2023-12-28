import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

import bot
from core import PathManager
from data_managers import DataUtils


def create_directories():
    os.makedirs(PathManager.DATA_DIR, exist_ok=True)
    os.makedirs(PathManager.TEMP_DIR, exist_ok=True)


async def main():
    # Set the project root first
    PathManager.set_project_root(Path(__file__).resolve().parent.parent)
    os.chdir(PathManager.PROJECT_ROOT)

    # Create directories if they are not created
    create_directories()

    # Load environment variables
    load_dotenv(dotenv_path=PathManager.DOT_ENV)

    # Set up my_logging
    import my_logging.setup_logging
    my_logging.setup_logging.main()

    # Create all resources
    from factories import UtilsFactory
    await UtilsFactory.create_all_instances()
    DataUtils.create_files()

    # Check paths existence
    PathManager.check_paths_existence()

    # Start the bot
    await bot.main()


if __name__ == "__main__":
    asyncio.run(main())
