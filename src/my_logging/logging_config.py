import sys

from core import PathManager

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
        'args': (sys.stdout,)
    },
    'root_file': {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'when': 'midnight',
        'interval': 1,
        'backupCount': 7,
        'formatter': 'file',
        'args': (f'{PathManager.LOGS_DIR}/root/root.log',)
    },
    'osu_api_file': {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'when': 'midnight',
        'interval': 1,
        'backupCount': 7,
        'formatter': 'osu_api',
        'args': (f'{PathManager.LOGS_DIR}/osu_api/osu_api.log',)
    },
    'data_utilities_file': {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'when': 'midnight',
        'interval': 1,
        'backupCount': 7,
        'formatter': 'file',
        'args': (f'{PathManager.LOGS_DIR}/data_utilities/data_utilities.log',)
    },
    'database_utilities_file': {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'when': 'midnight',
        'interval': 1,
        'backupCount': 7,
        'formatter': 'file',
        'args': (f'{PathManager.LOGS_DIR}/database_utilities/database_utilities.log',)
    }
}

formatters = {
    'file': {
        'format': '%(asctime)s - %(name)s - %(funcName)s - [%(levelname)s] - %(message)s'
    },
    'console': {
        'format': '%(asctime)s - %(name)s - %(funcName)s - [%(levelname)s] - %(message)s'
    },
    'osu_api': {
        'format': '%(asctime)s - %(name)s - %(funcName)s - [%(levelname)s] - %(message)s - tokens_spent=%(tokens_spent)s'
    }
}
