import logging.config
import os


def create_log_directories():
    log_directories = ['../logs', '../logs/root', '../logs/osu_api', '../logs/data_utilities',
                       '../logs/database_utilities']

    for directory in log_directories:
        os.makedirs(directory, exist_ok=True)


def main():
    create_log_directories()
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
    logging.config.fileConfig(log_file_path)
