import time


class RateLimiter:
    def __init__(self, max_requests, time_period):
        self.max_requests = max_requests
        self.time_period = time_period
        self.tokens = max_requests
        self.last_refill_time = time.time()

    def _refill_tokens(self):
        current_time = time.time()
        time_passed = current_time - self.last_refill_time
        tokens_to_add = int(time_passed / self.time_period)

        if tokens_to_add > 0:
            self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
            self.last_refill_time = current_time

    def can_make_request(self):
        self._refill_tokens()
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False
