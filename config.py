# config.py
import os
import time
import socket
import logging
import logging.handlers
from requests.exceptions import RequestException
from selenium.common.exceptions import TimeoutException
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# Configure logging
def setup_logging(log_file='crawler.log', console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Set up logging configuration with both console and file handlers.
    
    Args:
        log_file: Path to the log file
        console_level: Logging level for console output
        file_level: Logging level for file output
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all logs at the root level
    
    # Clear any existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Initialize logging
logger = logging.getLogger(__name__)

# API configuration
API_CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "openai_temperature": 0,
}

# Bright Data configuration
BRIGHT_DATA_CONFIG = {
    "server_addr": os.getenv("BRIGHT_DATA_SERVER_ADDR", 'https://brd-customer-hl_cf240944-zone-scrape_job_postings:si9klwfh7f28@brd.superproxy.io:9515')
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
