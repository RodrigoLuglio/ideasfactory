"""
Base screen classes and utilities for IdeasFactory UI.
"""

import logging
from typing import Optional, Dict, Any, List
import asyncio

from textual.screen import Screen

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)

class BaseScreen(Screen):
    """
    Base screen class with common functionality for IdeasFactory screens.
    
    Provides session handling and document loading capabilities.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the base screen."""
        super().__init__(*args, **kwargs)
        self.session_manager = SessionManager()
        self.session_id: Optional[str] = None
        self._is_mounted = False
        
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        
    def set_session(self, session_id: str) -> None:
        """
        Set the current session ID.
        
        Args:
            session_id: Session ID to set
        """
        # Store locally
        self.session_id = session_id
        
        # Update session manager if needed
        self.session_manager.set_current_session(session_id)
        
        # Load session documents if screen is mounted
        if self._is_mounted:
            asyncio.create_task(self._load_session_documents())
    
    @handle_async_errors
    async def _load_session_documents(self) -> None:
        """
        Load documents for the current session.
        
        This default implementation does nothing and should be overridden by subclasses.
        """
        pass
        
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Get the current session from the session manager
        current_session = self.session_manager.get_current_session()
        
        if current_session:
            # Only update if session has changed
            if not self.session_id or current_session.id != self.session_id:
                self.session_id = current_session.id
                
                # Load documents
                await self._load_session_documents()
        else:
            # No session
            self.session_id = None
            logger.warning("No active session when resuming screen")
            # Screens should override to provide appropriate UI updates