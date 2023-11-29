import asyncio
import time


class LeakyBucketRateLimiter:
    def __init__(self, tokens_per_second: float, max_tokens: float):
        self.tokens_per_second = tokens_per_second
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_refill_time = time.monotonic()
        self.queue = asyncio.Queue()

    def _refill_bucket(self):
        current_time = time.monotonic()
        elapsed_time = current_time - self.last_refill_time
        tokens_to_add = elapsed_time * self.tokens_per_second
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill_time = current_time

    def _can_make_request(self, tokens_required: float = 1):
        self._refill_bucket()
        if self.tokens >= tokens_required:
            self.tokens -= tokens_required
            return True
        else:
            return False

    async def wait_for_request(self, tokens_required: float):
        if not self._can_make_request(tokens_required):
            await self._enqueue_request(tokens_required)
            await self._process_queue()

    async def _enqueue_request(self, tokens_required: float):
        await self.queue.put(tokens_required)

    async def _process_queue(self):
        while not self.queue.empty() and self.tokens >= self.queue._get()[0]:
            request_tokens = self.queue._get()[0]
            self.tokens -= request_tokens
            await self.queue.get()
            self._refill_bucket()
