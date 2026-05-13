import asyncio
import time
from functools import wraps
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retry_on: tuple = (Exception,),
) -> Callable:
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Factor to multiply delay by after each failure
        max_delay: Maximum delay between retries
        retry_on: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise RetryError(f"Failed after {max_retries + 1} attempts: {e}") from e

                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise RetryError(f"Failed after {max_retries + 1} attempts: {e}") from e

                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_batch_operation(operation_func: Callable, batch_items: list, max_concurrent: int = 3) -> list:
    """
    Execute a batch operation with concurrent processing and individual retry logic.

    Args:
        operation_func: Function to execute for each item (should be decorated with retry logic)
        batch_items: List of items to process
        max_concurrent: Maximum number of concurrent operations

    Returns:
        List of results/errors for each item
    """
    import concurrent.futures
    import threading

    results = []
    lock = threading.Lock()

    def process_item(item):
        try:
            result = operation_func(item)
            with lock:
                results.append({"item": item, "success": True, "result": result})
        except Exception as e:
            with lock:
                results.append({"item": item, "success": False, "error": str(e)})

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = [executor.submit(process_item, item) for item in batch_items]
        concurrent.futures.wait(futures)

    return results