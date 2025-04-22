# src/ideasfactory/utils/__init__.py

"""
Utility modules for IdeasFactory.
"""


from typing import Optional
import logging

# Import key utility classes for easier access
from ideasfactory.utils.file_manager import load_document_content
from ideasfactory.utils.log_utils import (
    get_safe_env_vars, sanitize_environment_variables, is_sensitive_variable
)

# Configure logging
logger = logging.getLogger(__name__)

# Add to utils/__init__.py
from ideasfactory.utils.error_handler import (
    handle_errors, handle_async_errors, safe_execute, safe_execute_async, AppError
)
from ideasfactory.utils.session_manager import SessionManager, Session

from ideasfactory.utils.file_manager import load_document_content

# Add to utils/__init__.py
def validate_session(app, screen_name: str) -> Optional[str]:
    """
    Validate that a session exists for the current screen.
    
    Args:
        app: The application instance
        screen_name: Name of the current screen
        
    Returns:
        Session ID if valid, None otherwise
    """
    session_manager = SessionManager()
    current_session = session_manager.get_current_session()
    
    if not current_session:
        app.notify(f"No active session for {screen_name}", severity="error")
        logger.error(f"No active session when loading {screen_name}")
        return None
    
    return current_session.id