import asyncio
import time


class LeakyBucketRateLimiter:
    """
    Class to rate limit the 'OsuApiUtils' class using leaky bucket approach.
    """

    def __init__(self, tokens_per_second: float, max_tokens: float):
        self.tokens_per_second: float = tokens_per_second
        self.max_tokens: float = max_tokens
        self.tokens: float = max_tokens
        self.last_refresh_time: float = time.monotonic()
        self.queue = asyncio.Queue()

    async def _refresh_tokens(self):
        """
        Refreshes the amount of tokens available at the moment.
        """
        current_time = time.monotonic()
        time_elapsed = current_time - self.last_refresh_time
        self.tokens = min(self.tokens + time_elapsed * self.tokens_per_second, self.max_tokens)
        self.last_refresh_time = current_time

    async def _consume_tokens(self, tokens_required: float):
        """
        Consumes required amount of tokens.
        """
        if tokens_required > self.max_tokens:
            raise RuntimeError("The amount of tokens required cannot be greater than the 'max_tokens'")

        while self.tokens < tokens_required:
            await self._refresh_tokens()
            await asyncio.sleep(1 / self.tokens_per_second)
        self.tokens -= tokens_required

    async def _process_queue(self):
        """
        Processes the queue.
        """
        while not self.queue.empty():
            tokens_required = self.queue.get_nowait()
            await self._consume_tokens(tokens_required)

    async def process_request(self, tokens_required: float):
        """
        Processes the request.
        """
        await self.queue.put(tokens_required)
        await self._process_queue()
