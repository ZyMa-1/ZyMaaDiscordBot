from os import PathLike

from core import PathManager


def _construct_file_handler(formatter: str, filename: PathLike[str]) -> dict:
    return {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'when': 'midnight',
        'interval': 1,
        'backupCount': 7,
        'formatter': formatter,
        'filename': filename,
    }


def _get_default_format() -> str:
    return '%(asctime)s - %(name)s - %(funcName)s - [%(levelname)s] - %(message)s'


loggers = {
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'root_file']
    },
    'osu_api': {
        'level': 'INFO',
        'handlers': ['osu_api_file'],
        'qualname': 'osu_api'
    },
    'data_utilities': {
        'level': 'INFO',
        'handlers': ['data_utilities_file'],
        'qualname': 'data_utilities'
    },
    'database_utilities': {
        'level': 'INFO',
        'handlers': ['database_utilities_file'],
        'qualname': 'database_utilities'
    }
}

handlers = {
    'console': {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'console',
        'stream': 'ext://sys.stdout',
    },
    'root_file': _construct_file_handler('file', PathManager.ROOT_LOG),
    'osu_api_file': _construct_file_handler('osu_api', PathManager.OSU_API_LOG_DIR),
    'data_utilities_file': _construct_file_handler('file', PathManager.DATA_UTILITIES_LOG),
    'database_utilities_file': _construct_file_handler('file', PathManager.DATABASE_UTILITIES_LOG)
}

formatters = {
    'file': {
        'format': _get_default_format()
    },
    'console': {
        'format': _get_default_format()
    },
    'osu_api': {
        'format': f'{_get_default_format()} - tokens_spent=%(tokens_spent)s'
    }
}
