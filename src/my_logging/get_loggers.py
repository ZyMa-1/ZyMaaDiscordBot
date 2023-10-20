import logging


def osu_api_logger():
    return logging.getLogger('osu_api')


def data_utilities_logger():
    return logging.getLogger('data_utilities')


def database_utilities_logger():
    return logging.getLogger('database_utilities')
