# config.py
import os
import time
import socket
from requests.exceptions import RequestException
from selenium.common.exceptions import TimeoutException
from functools import wraps
import logging
from dotenv import load_dotenv

load_dotenv()

# logging
logger = logging.getLogger(__name__)

# API configuration
API_CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "openai_temperature": 0,
}

# decorators
def retry_with_backoff(max_tries=3, backoff_factor=2):
    """
    Retry decorator with exponential backoff for network operations.
    This covers typical transient errors (e.g., HTTP timeouts).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except (RequestException, socket.error, TimeoutException) as e:
                    if attempt == max_tries - 1:
                        logger.error(f"Failed after {max_tries} attempts: {str(e)}")
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Attempt {attempt+1} failed: {str(e)}. Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
        return wrapper
    return decorator
