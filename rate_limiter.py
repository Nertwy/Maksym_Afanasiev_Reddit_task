import asyncio
import random
import functools
from logging import Logger
from typing import Callable, TypeVar, Awaitable
from main_types import Args, Kwargs

from requests.exceptions import RequestException
from asyncprawcore.exceptions import ResponseException

T = TypeVar('T')


class APIRateLimiter:
    """
    A rate limiter for handling API requests with exponential backoff and concurrent request limiting.

    Attributes:
        max_retries (int): Maximum number of retry attempts
        initial_delay (float): Initial delay in seconds before retrying
        semaphore (asyncio.Semaphore): Semaphore for limiting concurrent requests
        logger (Logger): Logger instance for recording rate limit events
    """

    def __init__(self, logger: Logger, max_retries: int = 3,
                 initial_delay: float = 1.0, max_concurrent_requests: int = 50) -> None:
        """
        Initialize the rate limiter.

        Args:
            logger: Logger instance for recording events
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before retrying
            max_concurrent_requests: Maximum number of concurrent requests allowed
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.logger = logger

    async def wait_with_jitter(self, retries: int, base_delay: float) -> None:
        """
        Wait for a specified time with added random jitter.

        Args:
            retries: Current retry attempt number
            base_delay: Base delay time in seconds
        """
        delay = base_delay * (2 ** (retries - 1))
        jitter = random.uniform(0, delay * 0.1)
        wait_time = delay + jitter
        self.logger.warning(
            f"Rate limit hit. Waiting {wait_time:.2f} seconds before retry {retries}")
        await asyncio.sleep(wait_time)

    def rate_limit(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """
        Decorator that implements rate limiting with exponential backoff.

        Args:
            func: The async function to be rate limited

        Returns:
            A wrapped version of the function with rate limiting
        """
        @functools.wraps(func)
        async def wrapper(*args: Args, **kwargs: Kwargs) -> T:
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
                            self.logger.error(
                                f"Max retries ({self.max_retries}) exceeded for {args[1]}.")
                            raise e
                        await self.wait_with_jitter(retries, self.initial_delay)
            return await func(*args, **kwargs)
        return wrapper
