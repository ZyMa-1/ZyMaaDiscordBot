from functools import wraps
import time

import my_logging.get_loggers

logger = my_logging.get_loggers.database_utilities_logger()


def elapsed_time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.info(f"Function '{func.__name__}' took {elapsed_time:.6f} seconds")
        return result

    return wrapper
