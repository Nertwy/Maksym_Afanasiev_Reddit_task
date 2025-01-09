import asyncio
import random
import functools
from logging import Logger
from typing import Any, Callable
from requests.exceptions import RequestException
from asyncprawcore.exceptions import ResponseException

class APIRateLimiter:
    def __init__(self, logger:Logger,max_retries: int = 3, initial_delay: float = 1.0, max_concurrent_requests: int = 10):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.logger = logger

    async def wait_with_jitter(self, retries: int, base_delay: float) -> None:
        delay = base_delay * (2 ** (retries - 1))
        jitter = random.uniform(0, delay * 0.1)
        wait_time = delay + jitter
        self.logger.warning(f"Rate limit hit. Waiting {wait_time:.2f} seconds before retry {retries}")
        await asyncio.sleep(wait_time)
    
    def rate_limit(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            retries = 0
            while retries <= self.max_retries:
                async with self.semaphore:
                    try:
                        return await func(*args, **kwargs)
                    except (ResponseException, RequestException) as e:
                        if isinstance(e, ResponseException) and e.response.status != 429:
                            raise e
                        retries += 1
                        if retries > self.max_retries:
                            self.logger.error(f"Max retries ({self.max_retries}) exceeded for {args[1]}.")
                            raise e
                        await self.wait_with_jitter(retries, self.initial_delay)
            return await func(*args, **kwargs)
        return wrapper