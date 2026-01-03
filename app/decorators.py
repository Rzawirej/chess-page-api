import time
import logging
from typing import Callable
from functools import wraps

def log_execution_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logging.info(f"{func.__name__} execution time: {elapsed_time:.2f} seconds")
        return result
    return wrapper
