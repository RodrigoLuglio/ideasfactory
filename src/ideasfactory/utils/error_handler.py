# In src/ideasfactory/utils/error_handler.py

"""
Error handling utilities for IdeasFactory.

This module provides consistent error handling across the application.
"""

import logging
import traceback
import functools
import asyncio
from typing import Callable, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception class for application errors."""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)

def handle_errors(func):
    """Decorator to handle errors in functions and methods."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(traceback.format_exc())
            
            # If first arg is a screen or widget with notify method, use it
            if args and hasattr(args[0], "notify"):
                args[0].notify(f"Error: {str(e)}", severity="error")
            
            # Re-raise for higher-level handling
            raise
    return wrapper

def handle_async_errors(func):
    """Decorator to handle errors in async functions and methods."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(traceback.format_exc())
            
            # If first arg is a screen or widget with notify method, use it
            if args and hasattr(args[0], "notify"):
                args[0].notify(f"Error: {str(e)}", severity="error")
            
            # Re-raise for higher-level handling
            raise
    return wrapper

def safe_execute(action: Callable, error_message: str, notify_obj=None):
    """
    Execute a function safely with error handling.
    
    Args:
        action: Function to execute
        error_message: Message to log/display on error
        notify_obj: Object with notify method to show error messages
    
    Returns:
        Result of the function or None on error
    """
    try:
        return action()
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}")
        logger.debug(traceback.format_exc())
        
        if notify_obj and hasattr(notify_obj, "notify"):
            notify_obj.notify(f"{error_message}: {str(e)}", severity="error")
        
        return None

async def safe_execute_async(action: Callable, error_message: str, notify_obj=None):
    """
    Execute an async function safely with error handling.
    
    Args:
        action: Async function to execute
        error_message: Message to log/display on error
        notify_obj: Object with notify method to show error messages
    
    Returns:
        Result of the function or None on error
    """
    try:
        if asyncio.iscoroutinefunction(action) or asyncio.iscoroutine(action):
            return await action()
        else:
            return action()
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}")
        logger.debug(traceback.format_exc())
        
        if notify_obj and hasattr(notify_obj, "notify"):
            notify_obj.notify(f"{error_message}: {str(e)}", severity="error")
        
        return None