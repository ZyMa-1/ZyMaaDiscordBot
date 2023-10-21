import asyncio
import time


class TokenBucketRateLimiter:
    def __init__(self, tokens_per_second: float):
        self.tokens_per_second = tokens_per_second
        self.bucket_capacity = tokens_per_second
        self.tokens = 0
        self.last_refill_time = time.time()

    def _refill_bucket(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_refill_time
        tokens_to_add = elapsed_time * self.tokens_per_second
        self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)
        self.last_refill_time = current_time

    def _can_make_request(self, tokens_required: float = 1):
        self._refill_bucket()
        if self.tokens >= tokens_required:
            self.tokens -= tokens_required
            return True
        else:
            return False

    def _time_to_next_request(self, tokens_required: float = 1):
        self._refill_bucket()
        if self.tokens >= tokens_required:
            return 0  # No need to wait
        else:
            return (tokens_required - self.tokens) / self.tokens_per_second

    async def wait_for_request(self, tokens_required: float = 1):
        if not self._can_make_request(tokens_required):
            await asyncio.sleep(self._time_to_next_request(tokens_required))
