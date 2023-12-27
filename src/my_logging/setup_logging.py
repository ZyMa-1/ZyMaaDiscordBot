import logging.config
import os

import my_logging.logging_config as logging_config
from core import PathManager


def init_config():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': logging_config.loggers,
        'handlers': logging_config.handlers,
        'formatters': logging_config.formatters
    })


def create_log_directories():
    logs_dir = PathManager.LOGS_DIR
    log_directories = [logs_dir,
                       logs_dir / 'root',
                       logs_dir / 'osu_api',
                       logs_dir / 'data_utilities',
                       logs_dir / 'database_utilities']

    for directory in log_directories:
        os.makedirs(directory, exist_ok=True)


def main():
    init_config()
    create_log_directories()
    # ini_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
    # logging.config.fileConfig(ini_file_path)
