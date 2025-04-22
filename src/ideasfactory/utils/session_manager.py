# In src/ideasfactory/utils/session_manager.py

"""
Session management utilities for IdeasFactory.

This module provides a centralized session manager for the application.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from datetime import datetime
from ideasfactory.utils.error_handler import handle_errors

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class Session:
    """Class representing a user session."""
    id: str
    project_name: str
    creation_time: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    documents: Dict[str, str] = field(default_factory=dict)  # Maps document types to paths

class SessionManager:
    """
    Centralized session manager for the application.
    
    Implemented as a singleton to ensure the same instance is shared across the application.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of SessionManager is created."""
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the session manager."""
        if not hasattr(self, '_initialized') or not self._initialized:
            self.sessions: Dict[str, Session] = {}
            self.current_session_id: Optional[str] = None
            self._initialized = True
    
    @handle_errors
    def create_session(self, project_name: str) -> str:
        """
        Create a new session.
        
        Args:
            project_name: Name of the project for this session
            
        Returns:
            The ID of the created session
        """
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, project_name=project_name)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        logger.info(f"Created new session: {session_id} for project: {project_name}")
        return session_id
    
    @handle_errors
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: ID of the session to get
            
        Returns:
            The session or None if not found
        """
        return self.sessions.get(session_id)
    
    @handle_errors
    def get_current_session(self) -> Optional[Session]:
        """
        Get the current session.
        
        Returns:
            The current session or None if no session is active
        """
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None
    
    @handle_errors
    def set_current_session(self, session_id: str) -> bool:
        """
        Set the current session.
        
        Args:
            session_id: ID of the session to set as current
            
        Returns:
            True if the session was found and set as current, False otherwise
        """
        if session_id in self.sessions:
            self.current_session_id = session_id
            logger.info(f"Set current session to: {session_id}")
            return True
        logger.error(f"Session not found: {session_id}")
        return False
    
    @handle_errors
    def add_document(self, session_id: str, document_type: str, document_path: str) -> bool:
        """
        Add a document to a session.
        
        Args:
            session_id: ID of the session
            document_type: Type of the document
            document_path: Path to the document
            
        Returns:
            True if the document was added, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False
        
        session.documents[document_type] = document_path
        logger.info(f"Added document of type {document_type} to session {session_id}")
        return True
    
    @handle_errors
    def get_document(self, session_id: str, document_type: str) -> Optional[str]:
        """
        Get a document path from a session.
        
        Args:
            session_id: ID of the session
            document_type: Type of the document
            
        Returns:
            Path to the document or None if not found
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        return session.documents.get(document_type)
    
    @handle_errors
    def update_workflow_state(self, session_id: str, state: str) -> None:
        """Update the workflow state for a session."""
        session = self.get_session(session_id)
        if session:
            if not hasattr(session, "workflow_states"):
                session.workflow_states = []
            session.workflow_states.append({
                "state": state,
                "timestamp": datetime.now().isoformat()
            })
            logger.info(f"Session {session_id} workflow state updated to: {state}")
        else:
            logger.error(f"Cannot update workflow state - session not found: {session_id}")

    