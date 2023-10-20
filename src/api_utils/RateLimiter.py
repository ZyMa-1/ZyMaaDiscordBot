import time
from functools import wraps


def rate_limit(max_requests: int, per_seconds: int):
    def decorator(func):
        last_request_times = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            last_request_times.append(now)

            # Prune old request times
            last_request_times[:] = [t for t in last_request_times if t > now - per_seconds]

            if len(last_request_times) > max_requests:
                time.sleep(last_request_times[0] + per_seconds - now)

            return func(*args, **kwargs)

        return wrapper

    return decorator
